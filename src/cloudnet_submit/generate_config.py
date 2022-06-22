import pkgutil
from pathlib import Path
from sys import stdout


def generate_config(src: str, trg: str) -> None:
    example_config = pkgutil.get_data("cloudnet_submit", src)
    if not isinstance(example_config, bytes):
        raise ValueError(f'Cannot read "{src}" properly')
    path = Path(trg)
    if path.exists():
        raise FileExistsError(
            f'Cannot generate a configuration file, "{path}" already exists.'
        )
    elif trg == "-":
        stdout.buffer.write(example_config)
    else:
        with path.open("wb") as f:
            f.write(example_config)
