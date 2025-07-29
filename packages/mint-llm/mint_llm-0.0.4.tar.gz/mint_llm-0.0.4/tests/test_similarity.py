import torch
from safetensors.torch import load_file, save_file

from mint.similarity import build_similarity


def test_build_similarity_builds_and_saves(tmp_path):
    """End‑to‑end test: builds W, returns it, and writes W.safetensors."""
    emb = torch.eye(3, dtype=torch.float32)
    emb_file = tmp_path / "emb.safetensors"
    save_file({"embedding": emb}, str(emb_file))

    out_dir = tmp_path / "mint_out"
    W = build_similarity(str(emb_file), output_dir=str(out_dir), r=3)

    # Returned tensor
    assert W is not None
    assert W.shape == (3, 3)
    assert torch.allclose(W, torch.eye(3, dtype=emb.dtype), atol=1e-6)

    # Written file matches
    saved_W = load_file(str(out_dir / "W.safetensors"))["W"]
    assert torch.allclose(saved_W, W)


def test_build_similarity_dry_run(tmp_path, capsys):
    """--dry-run prints estimates and writes nothing."""
    emb = torch.randn(4, 2)
    emb_file = tmp_path / "emb.safetensors"
    save_file({"embedding": emb}, str(emb_file))

    out_dir = tmp_path / "dryrun_out"
    result = build_similarity(str(emb_file), output_dir=str(out_dir), dry_run=True)

    captured = capsys.readouterr()
    assert "dry-run" in captured.out.lower()
    assert result is None
    assert not (out_dir / "W.safetensors").exists()


def test_build_similarity_with_residual(tmp_path):
    """When keep_residual=True, residual file may be omitted if empty."""
    emb = torch.eye(2)
    emb_file = tmp_path / "emb.safetensors"
    save_file({"embedding": emb}, str(emb_file))

    out_dir = tmp_path / "residual_out"
    build_similarity(
        str(emb_file),
        output_dir=str(out_dir),
        r=2,
        keep_residual=True,
        residual_eps=0.1,
    )

    assert (out_dir / "W.safetensors").exists()
    assert (out_dir / "R.safetensors").exists()


def test_build_similarity_without_residual(tmp_path):
    """When keep_residual=True, residual file may be omitted if empty."""
    emb = torch.eye(2)
    emb_file = tmp_path / "emb.safetensors"
    save_file({"embedding": emb}, str(emb_file))

    out_dir = tmp_path / "residual_out"
    build_similarity(
        str(emb_file),
        output_dir=str(out_dir),
        r=2,
        keep_residual=False,
    )

    assert (out_dir / "W.safetensors").exists()
    assert not (out_dir / "R.safetensors").exists()
