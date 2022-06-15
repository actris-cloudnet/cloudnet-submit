import pytest

from cloudnet_submit.main import main


@pytest.mark.xfail
def test_test():
    main()
    assert True is True
