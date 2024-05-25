import docker
import pytest

from config import Config
from service_manager.docker_manager import DockerManager


@pytest.fixture(scope="package")
def config():
    config = Config()
    return config


@pytest.fixture(scope="module")
def manager(config):
    manager = DockerManager(
        config.service_name, config.input_directory,
        config.output_directory, config.port,
        False, False
    )
    return manager


@pytest.fixture
def client():
    client = docker.from_env()
    return client

