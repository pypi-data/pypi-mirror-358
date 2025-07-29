from typer.testing import CliRunner

from mint.cli import app


def test_cli_brew(monkeypatch):
    runner = CliRunner()

    called: dict[str, tuple[object, ...]] = {}

    def fake_load(model, sim, a):
        called["load"] = (model, sim, a)

        class Layer:
            def __call__(self, scores):
                return scores

        return object(), object(), Layer()

    def fake_pipeline(task, model=None, tokenizer=None, device=-1):
        called["pipeline"] = (task, model, tokenizer, device)

        def run(prompt, logits_processor=None):
            return [{"generated_text": f"echo: {prompt}"}]

        return run

    monkeypatch.setattr("mint.cli.load_wrapped_model", fake_load)

    class FakeProcessor:
        def __init__(self, layer, alpha=0.0):
            called["proc"] = alpha

        def __call__(self, *_):
            return []

    monkeypatch.setattr("mint.cli.pipeline", fake_pipeline)
    monkeypatch.setattr("mint.cli.SRLogitsProcessor", FakeProcessor)

    result = runner.invoke(
        app,
        [
            "brew",
            "dummy",
            "simdir",
            "--prompt",
            "hi",
            "--alpha",
            "0.5",
        ],
    )

    assert result.exit_code == 0
    assert "echo: hi" in result.stdout
    assert called["load"] == ("dummy", "simdir", 0.5)
    assert called["proc"] == 0.5
    assert called["pipeline"][0] == "text-generation"


def test_cli_brew_interactive(monkeypatch):
    runner = CliRunner()

    called: dict[str, tuple[object, ...]] = {}

    def fake_load(model, sim, a):
        called["load"] = (model, sim, a)

        class Layer:
            def __call__(self, scores):
                return scores

        return object(), object(), Layer()

    def fake_pipeline(task, model=None, tokenizer=None, device=-1):
        called["pipeline"] = (task, model, tokenizer, device)

        def run(prompt, logits_processor=None):
            return [{"generated_text": f"echo: {prompt}"}]

        return run

    monkeypatch.setattr("mint.cli.load_wrapped_model", fake_load)
    monkeypatch.setattr("mint.cli.pipeline", fake_pipeline)

    result = runner.invoke(
        app,
        ["brew", "dummy", "simdir", "--interactive"],
        input="hello\n\n",
    )

    assert result.exit_code == 0
    assert "echo: hello" in result.stdout
    assert called["load"] == ("dummy", "simdir", 0.0)
    assert called["pipeline"][0] == "text-generation"
