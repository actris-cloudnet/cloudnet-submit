import argparse
import pkgutil
from pathlib import Path
from sys import stdout

from .cfg import default_config_fname, example_config_fname


def generate_config() -> None:
    example_config = pkgutil.get_data("cloudnet_submit", example_config_fname)
    if not isinstance(example_config, bytes):
        raise ValueError(f'Cannot read "{example_config_fname}" properly')
    args = get_args()
    path = Path(args.output)
    if path.exists():
        raise FileExistsError(
            f'Cannot generate a configuration file, "{path}" already exists.'
        )
    elif args.output == "-":
        stdout.buffer.write(example_config)
    else:
        with path.open("wb") as f:
            f.write(example_config)


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--output", default=default_config_fname)
    return parser.parse_args()
