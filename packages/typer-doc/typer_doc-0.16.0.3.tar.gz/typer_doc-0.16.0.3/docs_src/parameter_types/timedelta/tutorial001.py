from datetime import timedelta

import typer


def main(delta: timedelta):
    if delta > timedelta(0):
        typer.echo(f"What a positive delta: {delta}!")
    else:
        typer.echo(f"What a negative delta: {delta}!")


if __name__ == "__main__":
    typer.run(main)
