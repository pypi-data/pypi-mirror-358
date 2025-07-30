import sys

import typer

if sys.version_info < (3, 8):
    from typing_extensions import Literal
else:
    from typing import Literal


def main(network: Literal["simple", "conv", "lstm"] = "simple"):
    print(f"Training neural network of type: {network}")


if __name__ == "__main__":
    typer.run(main)
