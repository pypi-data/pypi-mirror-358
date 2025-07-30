import sys
from typing import Union

import typer

if sys.version_info < (3, 8):
    from typing_extensions import Literal
else:
    from typing import Literal


def main(number: Union[int, Literal["-infinity", "infinity"]] = 0):
    if number == "infinity":
        print("Now that's a large number!")
    elif number == "-infinity":
        print("Now that's a small number!")
    else:
        print(f"{number} isn't all that small or large...")


if __name__ == "__main__":
    typer.run(main)
