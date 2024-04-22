import logging

import pytest

from docker_manager import DockerManager
import config


@pytest.fixture
def docker():
    docker = DockerManager(
        config.default_input_directory,
        config.default_output_directory,
        config.default_port
    )
    yield docker


def test_docker_manager_init(caplog):
    class_name = DockerManager.__class__.__name__
    image_name = f"{config.service_name}_image"
    expected_logs = (
        f"{class_name}: container_name: {config.service_name}",
        f"{class_name}: image_name: {image_name}",
        f"{class_name}: Input directory from user: {config.default_input_directory}",
        f"{class_name}: Output directory from user: {config.default_output_directory}",
        f"{class_name}: Port from user: {config.default_port}"
    )

    with caplog.at_level(logging.DEBUG):
        docker = DockerManager(
            config.default_input_directory,
            config.default_output_directory,
            config.default_port
        )

    assert docker.container_name == config.service_name
    assert docker.image_name == image_name
    assert docker.input_directory == config.default_input_directory
    assert docker.output_directory == config.default_output_directory
    assert docker.port == config.default_port
    for message in expected_logs:
        assert message in caplog.text, \
            f"Expected phrase not found in logs: {message}"
