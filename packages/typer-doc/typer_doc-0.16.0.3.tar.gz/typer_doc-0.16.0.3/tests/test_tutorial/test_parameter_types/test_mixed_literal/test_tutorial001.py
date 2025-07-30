import subprocess
import sys

import pytest
import typer
from typer.testing import CliRunner

from docs_src.parameter_types.mixed_literal import tutorial001 as mod

runner = CliRunner()

app = typer.Typer()
app.command()(mod.main)


def test_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "--number" in result.output
    assert "[-infinity|infinity]|INTEGER" in result.output
    assert "default: 0" in result.output


@pytest.mark.parametrize(
    "number, expected",
    [
        ("infinity", "Now that's a large number!"),
        ("-infinity", "Now that's a small number!"),
        ("123", "123 isn't all that small or large..."),
    ],
)
def test_main(number, expected):
    result = runner.invoke(app, ["--number", number])
    assert result.exit_code == 0
    assert expected in result.output


def test_main_default():
    result = runner.invoke(app)
    assert result.exit_code == 0
    assert "0 isn't all that small or large..." in result.output


def test_invalid_case():
    result = runner.invoke(app, ["--number", "i"])
    assert result.exit_code != 0

    # Choice failure
    assert "Invalid value for '--number'" in result.output
    assert "'i' is not one of" in result.output
    assert "-infinity" in result.output
    assert "infinity" in result.output

    # Integer failrue
    assert "'i' is not a valid integer" in result.output


def test_script():
    result = subprocess.run(
        [sys.executable, "-m", "coverage", "run", mod.__file__, "--help"],
        capture_output=True,
        encoding="utf-8",
    )
    assert "Usage" in result.stdout
