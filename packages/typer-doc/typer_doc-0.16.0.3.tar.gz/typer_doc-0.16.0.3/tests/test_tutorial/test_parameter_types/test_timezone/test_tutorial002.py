import subprocess

import typer
from typer.testing import CliRunner

from docs_src.parameter_types.timezone import tutorial002 as mod

runner = CliRunner()

app = typer.Typer()
app.command()(mod.main)


def test_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "TIMEZONE" in result.output


def test_main():
    result = runner.invoke(app, ["Asia/Dubai"])
    assert result.exit_code == 0
    assert "Time at Unix epoch was 04:00 in Asia/Dubai!" in result.output


def test_main_offset():
    result = runner.invoke(app, ["+240"])
    assert result.exit_code == 0
    assert "Time at Unix epoch was 04:00 in pytz.FixedOffset(240)!" in result.output


def test_invalid():
    result = runner.invoke(app, ["Asia/Abu_Dhabi"])
    assert result.exit_code != 0
    assert (
        "Invalid value for 'TIMEZONE': Unknown timezone or bad offset: Asia/Abu_Dhabi"
        in result.output
    )


def test_script():
    result = subprocess.run(
        ["coverage", "run", mod.__file__, "--help"],
        capture_output=True,
        encoding="utf-8",
    )
    assert "Usage" in result.stdout
