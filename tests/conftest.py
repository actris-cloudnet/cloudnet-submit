import pathlib
import shutil
import sys

import pytest
import requests

from .cfg import test_config_fname
from .generate_testdata import generate_testdata


@pytest.fixture
def make_test_dir(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)


@pytest.fixture
def make_test_dir_with_config(tmp_path, monkeypatch):
    cfg_path = pathlib.Path(__file__).parent.joinpath(test_config_fname)
    shutil.copy(cfg_path, tmp_path.joinpath(test_config_fname))
    monkeypatch.chdir(tmp_path)


@pytest.fixture
def make_data(make_test_dir_with_config):
    file_paths = generate_testdata()
    return file_paths


@pytest.fixture
def capture_stdout(monkeypatch):
    buffer = {"stdout": "", "calls": 0}

    def mock_write(s):
        buffer["stdout"] += s
        buffer["calls"] += 1

    monkeypatch.setattr(sys.stdout, "write", mock_write)
    return buffer


@pytest.fixture
def mock_request(monkeypatch):
    reqs = {"checksums": []}

    class Req:
        def __init__(self, ok=True, status_code=200):
            self.ok = ok
            self.status_code = status_code

    def mock_post(*args, **kwargs):
        reqs["checksums"].append(kwargs["json"]["checksum"])
        return Req()

    def mock_put(*args, **kwargs):
        return Req(status_code=201)

    monkeypatch.setattr(requests, "post", mock_post)
    monkeypatch.setattr(requests, "put", mock_put)
    return reqs
