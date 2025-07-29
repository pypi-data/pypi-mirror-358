from __future__ import annotations

from pathlib import Path
from safetensors.torch import load_file
import torch
from torch import nn

from .sr_layer import SimilarityRedistributor
from .low_rank_layer import LowRankRedistributor


def load_wrapped_model(
    model_path: str,
    similarity_path: str,
    alpha: float = 0.0,
) -> nn.Module:
    """Load a HuggingFace model and attach a ``SimilarityRedistributor``.

    Parameters
    ----------
    model_path:
        Either a Hugging Face model identifier or a local directory path
        understood by ``AutoModelForCausalLM.from_pretrained``.
    similarity_path:
        Directory containing ``W.safetensors`` or a file storing the sparse
        similarity matrix under the key ``"W"`` or ``"similarity"``.
    alpha:
        Strength of demotion for the original logits.
    """

    from transformers import AutoModelForCausalLM  # type: ignore

    model = AutoModelForCausalLM.from_pretrained(model_path)

    path = Path(similarity_path)
    if path.is_dir():
        path = path / "W.safetensors"
    if path.suffix == ".safetensors":
        state = load_file(str(path))
    else:
        state = torch.load(str(path))
    tensor = state["W"] if "W" in state else state["similarity"]
    layer: nn.Module
    if tensor.is_sparse:
        layer = SimilarityRedistributor(tensor, alpha=alpha)
    else:
        layer = LowRankRedistributor(tensor, alpha=alpha)
    if isinstance(model.lm_head, nn.Sequential):
        model.lm_head = nn.Sequential(*model.lm_head, layer)
    else:
        model.lm_head = nn.Sequential(model.lm_head, layer)
    return model
