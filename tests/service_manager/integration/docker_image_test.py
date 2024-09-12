import docker
import pytest

from config import Config


@pytest.fixture
def cleanup_docker_image(manager, client):
    image_name = manager.image_name
    try:
        client.images.remove(image_name, force=True)
    except docker.errors.ImageNotFound:
        pass

    yield

    try:
        client.images.remove(image_name, force=True)
    except docker.errors.ImageNotFound:
        pass


def test_build_image_and_docker_image_existence(cleanup_docker_image, manager, client):
    manager.build_image(Config.dockerfile)

    try:
        client.images.get(manager.image_name)
    except docker.errors.ImageNotFound:
        pytest.fail("Image was not built.")

    result = manager.docker_image_existence
    assert result is True


def test_docker_image_existence(cleanup_docker_image, manager):
    result = manager.docker_image_existence
    assert result is False
