import typer


def main(name: str):
    """Greet user.

    :param name: The name of the user to greet
    """
    print(f"Hello {name}")


if __name__ == "__main__":
    typer.run(main)
