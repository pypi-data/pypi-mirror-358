from __future__ import annotations
from pathlib import Path
from safetensors.torch import load_file, save_file
import torch  # type: ignore


def extract_embeddings(model_path: str, output_path: str) -> None:
    """Extract token embedding matrix from a checkpoint.

    Parameters
    ----------
    model_path:
        Path to the input checkpoint file.
    output_path:
        Destination file for the extracted embeddings in ``.safetensors``
        format.
    """

    path = Path(model_path)
    if path.name.endswith(".safetensors.index.json"):
        from .utils import load_sharded_state_dict

        state_dict = load_sharded_state_dict(str(path))
    elif path.suffix == ".safetensors":
        state_dict = load_file(str(path))
    else:
        state_dict = torch.load(str(path), map_location="cpu")

    candidates = {
        key: value
        for key, value in state_dict.items()
        if "embedding" in key or "embed_tokens" in key
    }
    if len(candidates) != 1:
        raise KeyError(f"Expected one embedding tensor, found {len(candidates)}")

    tensor = next(iter(candidates.values()))
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    save_file({"embedding": tensor}, str(output_path))
