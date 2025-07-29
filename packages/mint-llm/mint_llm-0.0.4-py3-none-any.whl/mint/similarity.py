from __future__ import annotations

from pathlib import Path
from safetensors.torch import load_file, save_file
from safetensors import safe_open
import torch  # type: ignore
from typing import Optional


def load_embeddings(path: str | Path, device: torch.device) -> torch.Tensor:
    state = load_file(str(Path(path)))
    if "embedding" not in state:
        raise KeyError("expected key `embedding`")
    return state["embedding"].to(device)


def normalize(E: torch.Tensor) -> torch.Tensor:
    return torch.nn.functional.normalize(E, p=2, dim=1)


def stream_covariance(E: torch.Tensor, block: int = 4096) -> torch.Tensor:
    n, d = E.shape
    C = torch.zeros(d, d, dtype=torch.float32, device=E.device)
    for s in range(0, n, block):
        blk = E[s : s + block]  # (b, d)
        C.addmm_(blk.t(), blk, beta=1.0, alpha=1.0)
    C = (C + C.t()).mul_(0.5)
    return C


def top_r_eigens(C: torch.Tensor, r: int):
    eigvals, eigvecs = torch.linalg.eigh(C)
    idx = eigvals.argsort(descending=True)[:r]
    Λ_r = eigvals[idx].clamp_min(0).sqrt()  # (r,)
    V_r = eigvecs[:, idx]  # (d, r)
    return V_r, Λ_r


def materialise_W(
    E: torch.Tensor,
    V_r: torch.Tensor,
    sqrtΛ: torch.Tensor,
    out_dtype: torch.dtype,
    block: int,
    out_path: Path,
) -> Optional[torch.Tensor]:
    """Builds **W**. If it fits (<2 GiB) keep in RAM and save once; otherwise
    streams blocks straight to *out_path* using ``safe_open(mode="wb")``.
    """

    n, _ = E.shape
    r = V_r.shape[1]
    bytes_need = n * r * torch.finfo(out_dtype).bits // 8
    RAM_LIMIT = 2 << 30  # 2 GiB

    V_scaled = V_r * sqrtΛ  # (d, r)

    if bytes_need <= RAM_LIMIT:
        # ------------------------------- in‑RAM path ---------------------------
        W_full = torch.empty((n, r), dtype=out_dtype, device=E.device)
        for s in range(0, n, block):
            blk = E[s : s + block]
            W_blk = blk @ V_scaled
            if out_dtype != W_blk.dtype:
                W_blk = W_blk.to(out_dtype)
            W_full[s : s + blk.shape[0]] = W_blk

        save_file({"W": W_full.cpu()}, str(out_path))
        return W_full.cpu()

        # ----------------------------- streamed path ------------------------------
    # The current safetensors API (<=0.3.x) has no incremental‑write mode.
    # We therefore **collect blocks on CPU**, concatenate once, then save –
    # still O(block) VRAM and only O(W) system RAM.

    blocks: list[torch.Tensor] = []
    for s in range(0, n, block):
        blk = E[s : s + block] @ V_scaled
        if out_dtype != blk.dtype:
            blk = blk.to(out_dtype)
        blocks.append(blk.cpu())  # free VRAM immediately

    W_full = torch.cat(blocks, dim=0)  # (n, r)
    save_file({"W": W_full}, str(out_path))
    return None


def write_residual_sparse(
    E: torch.Tensor,
    W: torch.Tensor,
    residual_eps: float,
    block: int,
    out_path: Path,
):
    """
    Streams residual R = K − W Wᵀ, keeping only entries |R| > eps.
    Saves as safetensors with COO format (`rows`, `cols`, `vals` tensors).
    """
    n = E.shape[0]
    device = E.device

    # Precompute global projection once (n, r)
    WT = W.to(device)  # ensure on same device
    rows_all, cols_all, vals_all = [], [], []

    for s in range(0, n, block):
        blk = E[s : s + block]  # (b, d)
        # Full cosine for the slice
        sim_blk = blk @ E.T  # (b, n)
        # Low-rank approximation
        W_blk = WT[s : s + block]  # (b, r)
        approx_blk = W_blk @ WT.T  # (b, n)

        resid = sim_blk.sub_(approx_blk)
        mask = resid.abs() > residual_eps
        local_r, local_c = mask.nonzero(as_tuple=True)
        if local_r.numel():
            rows_all.append(local_r + s)
            cols_all.append(local_c)
            vals_all.append(resid[local_r, local_c].to(E.dtype))

    if not rows_all:
        print("[mint] residual sparsification produced 0 nnz → skipped")
        save_file(
            {
                "rows": torch.tensor([], dtype=torch.int64),
                "cols": torch.tensor([], dtype=torch.int64),
                "vals": torch.tensor([], dtype=E.dtype),
            },
            str(out_path),
        )
        return

    rows = torch.cat(rows_all).cpu()
    cols = torch.cat(cols_all).cpu()
    vals = torch.cat(vals_all).cpu()

    save_file({"rows": rows, "cols": cols, "vals": vals}, str(out_path))
    print(
        f"[mint] residual R written → {out_path}  (nnz={vals.numel():,}, "
        f"≈{vals.numel() * torch.finfo(vals.dtype).bits // 8 / 1024**2:.1f} MiB)"
    )


def build_similarity(
    embedding_path: str | Path,
    output_dir: str | Path,
    r: int = 1024,
    block_size: int = 8192,
    keep_residual: bool = False,
    residual_eps: float = 1e-4,
    dry_run: bool = False,
    est_tflops: float = 25.0,
    device: str | torch.device | None = None,
) -> Optional[torch.Tensor]:
    """Build a low‑rank similarity factor **W** (and optional sparse residual **R**)
    from the embedding matrix stored in *embedding_path*.

    The function always **writes** ``W.safetensors`` into *output_dir*.
    If *keep_residual* is ``True`` it will also write ``R.safetensors``.

    Parameters
    ----------
    embedding_path : str | Path
        Safetensors file containing the "embedding" tensor (*n×d*).
    output_dir : str | Path
        Directory that will receive ``W.safetensors`` (and optionally
        ``R.safetensors``).
    r : int, default **1024**
        Target rank of the low‑rank factor.
    block_size : int, default **8192**
        Number of embedding rows processed per streaming block.
    keep_residual : bool, default **False**
        Write a sparse residual whenever |approx error| > *residual_eps*.
    residual_eps : float, default **1e-4**
        Threshold used when *keep_residual* is ``True``.
    dry_run : bool, default **False**
        If ``True`` perform no computation – merely print estimated peak
        RAM, output size, and runtime, then return ``None``.
    est_tflops : float, default **25.0**
        Sustained FP16/FP32 throughput used for runtime estimation in the
        *dry‑run* mode.
    device : str | torch.device | None
        Compute device; ``None`` selects CUDA when available.

    Returns
    -------
    torch.Tensor | None
        The in‑memory W tensor when it fits in RAM/VRAM; otherwise ``None``
        (the factor has been streamed directly to disk).
    """

    # ────────────────────────── lightweight header read ──────────────────────────
    with safe_open(str(embedding_path), framework="pt") as f:
        stub = f.get_tensor("embedding")  # mmap, cheap
        n, d = stub.shape
        dtype = stub.dtype

    # Map safetensors dtype strings → torch dtypes (fallback to getattr)
    _DTYPE_MAP = {
        "F16": torch.float16,
        "F32": torch.float32,
        "BF16": torch.bfloat16,
        "F64": torch.float64,
    }

    bytes_per_scalar = torch.finfo(dtype).bits // 8

    if dry_run:
        peak_ram = (
            2 * n * d * bytes_per_scalar  # full E
            + 4 * d * d  # covariance (fp32)
            + 2 * block_size * max(d, r) * bytes_per_scalar  # one work block
        )
        w_bytes = n * r * bytes_per_scalar
        flops = 2 * n * d * d + 2 * n * d * r + (2 / 3) * d * d * d
        eta = flops / (est_tflops * 1e12)

        print(
            f"[mint·dry-run] n={n:,}  d={d}  r={r}  block={block_size}"
            f"  • est peak RAM : {peak_ram / 1024**3:6.2f} GiB"
            f"  • W file size  : {w_bytes / 1024**2:6.2f} MiB"
            f"  • runtime (~{est_tflops} TFLOPs) : {eta:5.1f} s",
        )
        return None

    # ─────────────────────────────────────────────────────────────────────────────
    # heavy build starts here
    # ─────────────────────────────────────────────────────────────────────────────

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    W_path = output_dir / "W.safetensors"
    R_path = output_dir / "R.safetensors"

    device = torch.device(
        device
        if device is not None
        else ("cuda" if torch.cuda.is_available() else "cpu")
    )

    # 1) load + normalize embedding matrix
    E = load_embeddings(embedding_path, device)
    dtype_out = E.dtype
    E_norm = normalize(E)

    # 2) covariance → eigen decomposition
    C = stream_covariance(E_norm, block=block_size)
    V_r, sqrtΛ = top_r_eigens(C, r)

    # 3) build W in blocks
    W = materialise_W(
        E_norm,
        V_r.to(E_norm.dtype),
        sqrtΛ.to(E_norm.dtype),
        out_dtype=dtype_out,
        block=block_size,
        out_path=W_path,
    )

    # 4) optional residual tail
    if keep_residual:
        if W is None:  # streamed → reload for residual calc
            state = load_file(str(W_path))
            W = torch.cat([state[k] for k in sorted(state)]).to(device)
        else:
            W = W.to(device)

        write_residual_sparse(
            E_norm,
            W,
            residual_eps=residual_eps,
            block=block_size,
            out_path=R_path,
        )

    print(
        f"[mint] build complete → {W_path}"
        + (" & R.safetensors" if keep_residual else "")
    )

    return W
