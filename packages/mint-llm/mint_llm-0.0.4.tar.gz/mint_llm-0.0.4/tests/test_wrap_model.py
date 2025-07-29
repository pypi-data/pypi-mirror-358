import types
import sys
from typing import cast

import torch
from torch import nn
from safetensors.torch import save_file

from mint.low_rank_layer import LowRankRedistributor
from mint.wrap_model import load_wrapped_model


class DummyModel(nn.Module):
    def __init__(self) -> None:
        super().__init__()
        self.lm_head = nn.Identity()


class DummyModelLinear(nn.Module):
    def __init__(self) -> None:
        super().__init__()
        self.lm_head = nn.Linear(2, 2)


class DummyModelSequential(nn.Module):
    def __init__(self) -> None:
        super().__init__()
        self.lm_head = nn.Sequential(nn.Linear(2, 2), nn.ReLU())


class DummyAuto:
    model_cls: type[nn.Module] = DummyModel

    @classmethod
    def from_pretrained(cls, path: str) -> nn.Module:  # type: ignore[override]
        return cls.model_cls()


def install_dummy_transformers(monkeypatch, model_cls: type[nn.Module] = DummyModel):
    DummyAuto.model_cls = model_cls
    module = types.ModuleType("transformers")
    module.AutoModelForCausalLM = DummyAuto  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "transformers", module)


def test_load_wrapped_model_pt(monkeypatch, tmp_path):
    install_dummy_transformers(monkeypatch)
    S = torch.eye(2)
    sim_dir = tmp_path / "sim"
    sim_dir.mkdir()
    save_file({"W": S}, str(sim_dir / "W.safetensors"))

    model = load_wrapped_model("dummy", str(sim_dir), alpha=0.5)
    assert isinstance(model.lm_head, nn.Sequential)
    assert isinstance(model.lm_head[1], LowRankRedistributor)
    layer = cast(LowRankRedistributor, model.lm_head[1])
    assert layer.alpha == 0.5
    assert torch.equal(layer.W, torch.eye(2))


def test_load_wrapped_model_safetensors(monkeypatch, tmp_path):
    install_dummy_transformers(monkeypatch)
    S = torch.tensor([[0.0, 1.0], [1.0, 0.0]])
    sim_dir = tmp_path / "sim"
    sim_dir.mkdir()
    save_file({"W": S}, str(sim_dir / "W.safetensors"))

    model = load_wrapped_model("dummy", str(sim_dir))
    assert isinstance(model.lm_head, nn.Sequential)
    layer = cast(LowRankRedistributor, model.lm_head[1])
    assert isinstance(layer, LowRankRedistributor)
    assert torch.equal(layer.W, S)


def test_wrap_single_module(monkeypatch, tmp_path):
    install_dummy_transformers(monkeypatch, DummyModelLinear)
    S = torch.eye(2)
    sim_dir = tmp_path / "sim"
    sim_dir.mkdir()
    save_file({"W": S}, str(sim_dir / "W.safetensors"))

    model = load_wrapped_model("dummy", str(sim_dir))
    assert isinstance(model.lm_head, nn.Sequential)
    assert len(model.lm_head) == 2
    assert isinstance(model.lm_head[0], nn.Linear)
    assert isinstance(model.lm_head[1], LowRankRedistributor)


def test_wrap_existing_sequential(monkeypatch, tmp_path):
    install_dummy_transformers(monkeypatch, DummyModelSequential)
    S = torch.eye(2)
    sim_dir = tmp_path / "sim"
    sim_dir.mkdir()
    save_file({"W": S}, str(sim_dir / "W.safetensors"))

    model = load_wrapped_model("dummy", str(sim_dir))
    assert isinstance(model.lm_head, nn.Sequential)
    assert len(model.lm_head) == 3
    assert isinstance(model.lm_head[-1], LowRankRedistributor)
    assert isinstance(model.lm_head[0], nn.Linear)
    assert isinstance(model.lm_head[1], nn.ReLU)
