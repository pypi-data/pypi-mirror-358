from typer.testing import CliRunner
import torch
from safetensors.torch import save_file, load_file

from mint.cli import app


def test_cli_blend_writes_W(tmp_path):
    runner = CliRunner()
    emb = torch.eye(3)
    emb_file = tmp_path / "emb.safetensors"
    save_file({"embedding": emb}, str(emb_file))

    out_dir = tmp_path / "out"
    result = runner.invoke(app, ["blend", str(emb_file), str(out_dir), "--rank", "2"])
    assert result.exit_code == 0
    W = load_file(str(out_dir / "W.safetensors"))["W"]
    assert W.shape == (3, 2)


def test_cli_blend_cpu_option(tmp_path):
    runner = CliRunner()
    emb = torch.eye(2)
    emb_file = tmp_path / "emb_cpu.safetensors"
    save_file({"embedding": emb}, str(emb_file))

    out_dir = tmp_path / "sim_cpu"
    result = runner.invoke(
        app, ["blend", str(emb_file), str(out_dir), "--rank", "1", "--cpu"]
    )
    assert result.exit_code == 0
    W = load_file(str(out_dir / "W.safetensors"))["W"]
    assert W.shape == (2, 1)


def test_cli_blend_creates_subdirs(tmp_path):
    runner = CliRunner()
    emb = torch.eye(2)
    emb_file = tmp_path / "emb.safetensors"
    save_file({"embedding": emb}, str(emb_file))

    out_dir = tmp_path / "nested"
    result = runner.invoke(app, ["blend", str(emb_file), str(out_dir), "--rank", "2"])
    assert result.exit_code == 0
    assert (out_dir / "W.safetensors").exists()
    W = load_file(str(out_dir / "W.safetensors"))["W"]
    assert W.shape == (2, 2)
