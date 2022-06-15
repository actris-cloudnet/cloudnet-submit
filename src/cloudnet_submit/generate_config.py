import argparse
from pathlib import Path
from sys import stderr, stdout

default_config = """\
[user_account]
username = "alice"
password = "alicesSecretPassword"

[[instrument]]
site       =  "mace-head"
instrument =  "chm15k"
path_fmt   =  "/data/hyytiala/chm15k/%Y/%m/hyytiala-chm15k-%Y-%m-%d*.nc"
"""


def generate_config() -> None:
    args = get_args()
    print(type(args))
    path = Path(args.output)
    if path.exists():
        stderr.write(
            f'Cannot generate a configuration file, "{path}" already exists.\n'
        )
    elif args.output == "-":
        stdout.write(default_config)
    else:
        with path.open("w") as f:
            f.write(default_config)


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--output", default="cloudnet-config.toml")
    return parser.parse_args()
