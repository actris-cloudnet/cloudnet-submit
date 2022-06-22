from unittest.mock import patch

import pytest

from cloudnet_submit.cfg import (
    default_config_fname,
    example_config_fname,
    get_config,
)
from cloudnet_submit.generate_config import generate_config
from cloudnet_submit.utils import get_submissions

from .cfg import test_config_fname


def test_generate_config(make_test_dir):
    generate_config(example_config_fname, "-")
    generate_config(example_config_fname, default_config_fname)
    with pytest.raises(FileExistsError):
        generate_config(example_config_fname, default_config_fname)


def test_submissions(make_data, mock_request):
    with patch("sys.argv", ["prog", "--config", test_config_fname]):
        config = get_config()
        submissions = get_submissions(config)
    generated_files = set([p.resolve() for p in make_data])
    files_to_submit = set([sub.path.resolve() for sub in submissions])
    assert len(generated_files) > 0
    assert generated_files == files_to_submit
    for s in sorted(submissions):
        s.dry_run()
    for s in sorted(submissions):
        s.submit()
    received_checksums = set(mock_request["checksums"])
    sent_checksums = set([s.metadata.checksum for s in submissions])
    assert len(received_checksums) == len(generated_files)
    assert received_checksums == sent_checksums
