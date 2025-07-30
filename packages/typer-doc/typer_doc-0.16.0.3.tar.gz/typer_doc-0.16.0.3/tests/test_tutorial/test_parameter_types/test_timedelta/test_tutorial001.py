import subprocess
from datetime import timedelta

import pytest
import typer
from typer.testing import CliRunner

from docs_src.parameter_types.timedelta import tutorial001 as mod

runner = CliRunner()

app = typer.Typer()
app.command()(mod.main)


def test_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "TIMEDELTA" in result.output


@pytest.mark.parametrize(
    "input_string, expected",
    [
        ("3:30:00", timedelta(hours=3, minutes=30)),
        ("3 hours 30 minutes", timedelta(hours=3, minutes=30)),
        ("3 hrs 30 minutes", timedelta(hours=3, minutes=30)),
        ("3hrs 30mins", timedelta(hours=3, minutes=30)),
        ("3h30m", timedelta(hours=3, minutes=30)),
        (
            "1 week 2 days 3 hours 4 minutes 5 seconds 6 milliseconds 7 microseconds",
            timedelta(
                weeks=1,
                days=2,
                hours=3,
                minutes=4,
                seconds=5,
                milliseconds=6,
                microseconds=7,
            ),
        ),
    ],
)
def test_main(input_string: str, expected: timedelta):
    result = runner.invoke(app, [input_string])
    assert result.exit_code == 0, result.output
    assert f"What a positive delta: {expected}!" in result.output


@pytest.mark.parametrize(
    "input_string",
    [
        "3:30",
        "10 minz",
        "1 day 3:30",
    ],
)
def test_invalid(input_string: str):
    result = runner.invoke(app, [input_string])
    assert result.exit_code != 0
    assert "Invalid value for 'DELTA':" in result.output


def test_script():
    result = subprocess.run(
        ["coverage", "run", mod.__file__, "--help"],
        capture_output=True,
        encoding="utf-8",
    )
    assert "Usage" in result.stdout
