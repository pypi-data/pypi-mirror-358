from __future__ import annotations

from torch import nn
import torch


class LowRankRedistributor(nn.Module):
    """Redistribute logits using a low-rank factor ``W``."""

    def __init__(self, W: torch.Tensor, alpha: float = 0.0) -> None:
        super().__init__()
        if W.ndim != 2:
            raise ValueError("W must be 2-D")
        self.W: torch.Tensor
        self.register_buffer("W", W)
        self.alpha = float(alpha)
        self.vocab_size = W.shape[0]

    def forward(self, logits: torch.Tensor) -> torch.Tensor:  # type: ignore[override]
        original_shape = logits.shape
        logits2d = logits.view(-1, self.vocab_size)
        tmp = logits2d @ self.W
        redistributed = tmp @ self.W.t()
        if self.alpha > 0:
            redistributed = redistributed - self.alpha * logits2d
        return redistributed.view(original_shape)
