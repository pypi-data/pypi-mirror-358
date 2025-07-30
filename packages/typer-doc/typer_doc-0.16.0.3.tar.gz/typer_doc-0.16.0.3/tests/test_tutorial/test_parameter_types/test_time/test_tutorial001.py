import subprocess

import pytest
import typer
from typer.testing import CliRunner

from docs_src.parameter_types.time import tutorial001 as mod

runner = CliRunner()

app = typer.Typer()
app.command()(mod.main)


def test_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "[%H:%M|%H:%M:%S]" in result.output


@pytest.mark.parametrize(
    "input_string",
    [
        "14:02:00",
        "14:02",
    ],
)
def test_main(input_string: str):
    result = runner.invoke(app, [input_string])
    assert result.exit_code == 0
    assert "Interesting time to be born: 14:02:00" in result.output
    assert "Born after midday!" in result.output


def test_invalid():
    result = runner.invoke(app, ["1402"])
    assert result.exit_code != 0
    assert (
        "Invalid value for 'BIRTH:[%H:%M|%H:%M:%S]': '1402' does not match the formats '%H:%M', '%H:%M:%S'."
        in result.output
    )


def test_script():
    result = subprocess.run(
        ["coverage", "run", mod.__file__, "--help"],
        capture_output=True,
        encoding="utf-8",
    )
    assert "Usage" in result.stdout
