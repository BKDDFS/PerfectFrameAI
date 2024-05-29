import docker
import pytest


@pytest.fixture
def image(client, manager, config):
    image_name = "image_name"
    image = client.images.pull("busybox")
    image.tag(image_name)
    manager._image_name = image_name
    yield image
    client.images.remove(image_name, force=True)


@pytest.fixture
def cleanup_container(client, manager, config):
    try:
        container = client.containers.get(manager._container_name)
        container.remove(force=True)
    except docker.errors.NotFound:
        pass
    yield
    try:
        container = client.containers.get(manager._container_name)
        container.remove(force=True)
    except docker.errors.NotFound:
        pass


def test_run_container(manager, config, client, cleanup_container, image):
    manager._run_container(config.port, config.volume_input_directory, config.volume_output_directory)

    container = client.containers.get(manager._container_name)
    container.reload()
    assert container.status == "running" or container.status == "restarting"
    assert container.attrs["Config"]["Image"] == manager.image_name
    port_binding = container.attrs["HostConfig"]["PortBindings"]
    assert '8100/tcp' in port_binding
    assert port_binding['8100/tcp'][0]['HostPort'] == str(config.port)
    assert f"{manager._input_directory}:{config.volume_input_directory}" in container.attrs["HostConfig"]["Binds"]
    assert f"{manager._output_directory}:{config.volume_output_directory}" in container.attrs["HostConfig"]["Binds"]


def test_start_container(manager, cleanup_container, client, image):
    container = client.containers.create(image, command="sleep 300", detach=True, name=manager._container_name)
    assert container.status == "created"
    manager._start_container()
    container.reload()
    assert container.status == "running"


def test_stop_container(manager, cleanup_container, client, image):
    container = client.containers.create(image, command="sleep 300", detach=True, name=manager._container_name)
    assert container.status == "created"
    container.start()
    container.reload()
    assert container.status == "running"
    manager._stop_container()
    container.reload()
    assert container.status == "exited"


def test_delete_container(manager, cleanup_container, client, image):
    container = client.containers.create(image, command="sleep 300", detach=True, name=manager._container_name)
    assert container.status == "created"
    manager._delete_container()
    with pytest.raises(docker.errors.NotFound):
        client.containers.get(manager._container_name)


def test_container_status(manager, cleanup_container, client, image):
    container = client.containers.create(image, command="sleep 300", detach=True, name=manager._container_name)
    assert container.status == "created"
    assert manager.container_status == "created"
    container.start()
    container.reload()
    assert container.status == "running"
    assert manager.container_status == "running"


def test_run_log_process(manager, cleanup_container, client, image):
    container = client.containers.run(
        image,
        command="sh -c 'while true; do date; done'",
        detach=True,
        name=manager._container_name
    )
    log_process = manager._run_log_process()
    assert log_process.poll() is None, "Log process should be running"
    output = []
    try:
        for _ in range(5):
            line = log_process.stdout.readline()
            output.append(line)
            assert line, "Log line should not be empty"
    finally:
        log_process.terminate()
        log_process.wait()
    assert len(output) >= 5, "Should have read at least 5 lines of logs"
