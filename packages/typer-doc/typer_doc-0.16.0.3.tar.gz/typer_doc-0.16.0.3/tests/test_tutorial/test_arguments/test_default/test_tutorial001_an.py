import subprocess
import sys

import pytest
import typer
from typer.testing import CliRunner

from docs_src.arguments.default import tutorial001_an as mod

runner = CliRunner()


@pytest.fixture(scope="module", params=["rich", "markdown", None])
def app(request: pytest.FixtureRequest):
    app = typer.Typer(rich_markup_mode=request.param)
    app.command()(mod.main)
    yield app


def test_help(app):
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "[OPTIONS] [NAME]" in result.output
    assert "Arguments" in result.output
    assert "[default: Wade Wilson]" in result.output


def test_call_no_arg(app):
    result = runner.invoke(app)
    assert result.exit_code == 0, result.output
    assert "Hello Wade Wilson" in result.output


def test_call_arg(app):
    result = runner.invoke(app, ["Camila"])
    assert result.exit_code == 0
    assert "Hello Camila" in result.output


def test_script(app):
    result = subprocess.run(
        [sys.executable, "-m", "coverage", "run", mod.__file__, "--help"],
        capture_output=True,
        encoding="utf-8",
    )
    assert "Usage" in result.stdout
