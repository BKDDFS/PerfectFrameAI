import docker
import pytest

from config import Config
from ..common import (
    files_dir, best_frames_dir, top_images_dir,
    setup_top_images_extractor_env, setup_best_frames_extractor_env
)  # import fixtures from common.py
from ...docker_manager import DockerManager


@pytest.fixture(scope="package")
def config():
    config = Config()
    return config


@pytest.fixture(scope="module")
def manager(config):
    manager = DockerManager(
        config.service_name, config.input_directory,
        config.output_directory, config.port, False
    )
    return manager


@pytest.fixture
def client():
    client = docker.from_env()
    return client

