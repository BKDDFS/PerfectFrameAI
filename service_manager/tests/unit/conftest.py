import pytest

from config import Config


@pytest.fixture(scope="package")
def config():
    return Config()
