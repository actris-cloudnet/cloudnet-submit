import datetime
import hashlib
from pathlib import Path


def compute_checksum(path: Path):
    BLOCK_SIZE = 512
    md5hash = hashlib.md5()
    with path.open("rb") as f:
        chunk = f.read(BLOCK_SIZE)
        while chunk:
            md5hash.update(chunk)
            chunk = f.read(BLOCK_SIZE)
    return md5hash.hexdigest()


def date_parser(date_str: str) -> datetime.date:
    return datetime.date.fromisoformat(date_str)
