import datetime

import pytz
import typer


def main(timezone: pytz.BaseTzInfo):
    time_at_epoch = datetime.datetime.fromtimestamp(0, tz=timezone)
    typer.echo(f"Time at Unix epoch was {time_at_epoch:%H:%M} in {timezone}!")


if __name__ == "__main__":
    typer.run(main)
