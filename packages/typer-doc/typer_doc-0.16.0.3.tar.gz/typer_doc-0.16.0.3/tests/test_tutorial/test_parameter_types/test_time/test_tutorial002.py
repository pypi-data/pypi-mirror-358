import subprocess

import pytest
import typer
from typer.testing import CliRunner

from docs_src.parameter_types.time import tutorial002 as mod

runner = CliRunner()

app = typer.Typer()
app.command()(mod.main)


@pytest.mark.parametrize(
    "input_string",
    [
        "14:02",
        "1402",
    ],
)
def test_main(input_string):
    result = runner.invoke(app, [input_string])
    assert result.exit_code == 0
    assert "Launch will be at: 14:02:00" in result.output


def test_alt_time_format():
    result = runner.invoke(app, ["1402"])
    assert result.exit_code == 0
    assert "Launch will be at: 14:02:00" in result.output


def test_script():
    result = subprocess.run(
        ["coverage", "run", mod.__file__, "--help"],
        capture_output=True,
        encoding="utf-8",
    )
    assert "Usage" in result.stdout
