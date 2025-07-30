from datetime import time

import typer


def main(birth: time):
    typer.echo(f"Interesting time to be born: {birth}")
    if birth >= time(12, 0):
        typer.echo("Born after midday!")
    else:
        typer.echo("Born before midday!")


if __name__ == "__main__":
    typer.run(main)
