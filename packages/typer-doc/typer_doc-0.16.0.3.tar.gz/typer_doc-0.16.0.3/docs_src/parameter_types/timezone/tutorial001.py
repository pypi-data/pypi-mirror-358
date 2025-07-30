import datetime
import sys

import typer

if sys.version_info < (3, 9):
    from backports.zoneinfo import ZoneInfo
else:
    from zoneinfo import ZoneInfo


def main(timezone: ZoneInfo):
    time_at_epoch = datetime.datetime.fromtimestamp(0, tz=timezone)
    typer.echo(f"Time at Unix epoch was {time_at_epoch:%H:%M} in {timezone}!")


if __name__ == "__main__":
    typer.run(main)
