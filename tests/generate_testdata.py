import datetime
import random
import string
from pathlib import Path

import toml

from .cfg import test_config_fname


def generate_testdata():
    cfg = toml.load(test_config_fname)
    path_fmts = []
    for c in cfg["instrument"] if "instrument" in cfg else []:
        path_fmts.append(c["path_fmt"])
    for c in cfg["model"] if "model" in cfg else []:
        path_fmts.append(c["path_fmt"])
    file_paths = []
    for fmt in path_fmts:
        file_paths.extend(generate_files_from_fmt(fmt))
    return file_paths


def generate_files_from_fmt(fmt):
    today = datetime.datetime.utcnow().date()
    one_day = datetime.timedelta(days=1)
    past_three_days = [today - i * one_day for i in reversed(range(3))]
    file_paths = []
    for day in past_three_days:
        path_glob = day.strftime(fmt)
        while "*" in path_glob:
            rnd_str = random_string(length=4)
            path_glob = path_glob.replace("*", rnd_str, 1)
        path_str = path_glob
        file_paths.append(generate_random_file(path_str))
    return file_paths


def generate_random_file(path_str: str) -> Path:
    path = Path(path_str)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        for _ in range(100):
            line = random_string(length=78)
            f.write(f"{line}\n")
    return path


def random_string(length=10):
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=length))
