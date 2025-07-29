import torch
from mint.low_rank_layer import LowRankRedistributor


def test_low_rank_basic_redistribution():
    W = torch.tensor([[1.0, 0.0], [0.0, 1.0], [0.0, 1.0]])
    layer = LowRankRedistributor(W)
    logits = torch.tensor([0.1, 0.2, 0.3])
    expected = W @ (W.t() @ logits)
    out = layer(logits)
    assert torch.allclose(out, expected)


def test_low_rank_alpha_demotion():
    W = torch.eye(2)
    layer = LowRankRedistributor(W, alpha=0.5)
    logits = torch.tensor([1.0, 2.0])
    redistributed = W @ (W.t() @ logits)
    expected = redistributed - 0.5 * logits
    out = layer(logits)
    assert torch.allclose(out, expected)
