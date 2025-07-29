from __future__ import annotations

from pathlib import Path
from typing import Tuple

from torch import nn

import torch
from safetensors.torch import load_file
from transformers import AutoModelForCausalLM, AutoTokenizer

from .sr_layer import SimilarityRedistributor
from .low_rank_layer import LowRankRedistributor


def _load_similarity(
    path: str, device: torch.device | str | None = None
) -> torch.Tensor:
    p = Path(path)
    if p.is_dir():
        p = p / "W.safetensors"
    if p.suffix == ".safetensors":
        state = load_file(str(p))
    else:
        state = torch.load(str(p))
    tensor = state["W"] if "W" in state else state["similarity"]
    if device is not None:
        tensor = tensor.to(device)
    return tensor


def load_wrapped_model(
    model_name_or_path: str, similarity: str, alpha: float = 0.0
) -> Tuple[AutoModelForCausalLM, AutoTokenizer, nn.Module]:
    """Load a model and attach the similarity redistribution layer.

    Parameters
    ----------
    model_name_or_path:
        Hugging Face model identifier or local path understood by
        ``AutoModelForCausalLM.from_pretrained``.
    similarity:
        Directory containing ``W.safetensors`` or a file with the sparse
        similarity matrix under the key ``"W"`` or ``"similarity"``.
    alpha:
        Strength of demotion for the original logits. ``0`` disables demotion.
    """

    model = AutoModelForCausalLM.from_pretrained(model_name_or_path)
    tokenizer = AutoTokenizer.from_pretrained(model_name_or_path)
    S = _load_similarity(similarity, model.device)
    layer: nn.Module
    if S.is_sparse:
        layer = SimilarityRedistributor(S, alpha=alpha)
    else:
        layer = LowRankRedistributor(S, alpha=alpha)
    return model, tokenizer, layer
