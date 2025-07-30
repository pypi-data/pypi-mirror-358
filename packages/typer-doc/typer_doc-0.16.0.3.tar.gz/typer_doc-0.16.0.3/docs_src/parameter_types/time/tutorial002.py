from datetime import time

import typer


def main(launch_time: time = typer.Argument(..., formats=["%H:%M", "%H%M"])):
    typer.echo(f"Launch will be at: {launch_time}")


if __name__ == "__main__":
    typer.run(main)
