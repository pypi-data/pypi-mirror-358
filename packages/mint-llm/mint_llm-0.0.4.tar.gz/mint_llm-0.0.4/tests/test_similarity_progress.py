import contextlib
from io import StringIO
from pathlib import Path

import torch
from safetensors.torch import save_file

from mint.similarity import build_similarity

CACHE_DIR = Path(__file__).resolve().parents[1] / ".cache" / "mint"


def test_build_similarity_uses_tqdm(tmp_path):
    emb = torch.eye(2)
    emb_file = tmp_path / "emb.safetensors"
    save_file({"embedding": emb}, str(emb_file))

    buf = StringIO()

    with contextlib.redirect_stdout(buf):
        build_similarity(str(emb_file), CACHE_DIR)

    assert "build complete" in buf.getvalue()
