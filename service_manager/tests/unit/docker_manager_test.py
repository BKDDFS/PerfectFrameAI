import logging
import subprocess
from unittest.mock import patch, MagicMock, PropertyMock, call

import pytest

from service_manager.docker_manager import DockerManager


def test_docker_manager_init(caplog, config):
    image_name = f"{config.service_name}_image"
    expected_logs = (
        f"container_name: {config.service_name}",
        f"image_name: {image_name}",
        f"Input directory from user: {config.input_directory}",
        f"Output directory from user: {config.output_directory}",
        f"Port from user: {config.port}",
        f"Force build: False"
    )

    with caplog.at_level(logging.DEBUG):
        docker = DockerManager(
            config.service_name, config.input_directory,
            config.output_directory, config.port, False
        )

    assert docker._container_name == config.service_name
    assert docker._image_name == image_name
    assert docker._input_directory == config.input_directory
    assert docker._output_directory == config.output_directory
    assert docker._port == config.port
    assert docker._force_build is False
    for message in expected_logs:
        assert message in caplog.text, \
            f"Expected phrase not found in logs: {message}"


@pytest.fixture(scope="function")
def docker(config):
    docker = DockerManager(
        config.service_name, config.input_directory,
        config.output_directory, config.port, False
    )
    return docker


@pytest.fixture(name="mock_run")
def mock_subprocess_run():
    with patch("service_manager.docker_manager.subprocess.run") as mock_run:
        yield mock_run


@pytest.mark.parametrize("mock_image, is_exists", (("some_image", True), ("", False)))
def test_check_image_exists(mock_image, is_exists, docker, mock_run):
    expected_command = ["docker", "images", "-q", docker._image_name]

    mock_run.return_value = MagicMock(stdout=mock_image)
    assert docker.docker_image_existence is is_exists
    mock_run.assert_called_with(expected_command, capture_output=True, text=True)


@patch.object(DockerManager, "_check_image_exists")
def test_build_image(mock_check_image_exists, docker, mock_run, caplog, config):
    mock_check_image_exists.return_value = False
    expected_command = ["docker", "build", "-t", docker._image_name, config.dockerfile]

    docker.build_image(config.dockerfile)

    mock_run.assert_called_once_with(expected_command)


@patch.object(DockerManager, "_check_image_exists")
def test_build_image_when_image_exists_and_not_force_build(
        mock_check_image_exists, docker, mock_run, caplog, config):
    mock_check_image_exists.return_value = True

    with caplog.at_level(logging.INFO):
        docker.build_image(config.dockerfile)

    mock_run.assert_not_called()
    assert "Image is already created. Using existing one." in caplog.text


@patch.object(DockerManager, "_check_image_exists")
def test_build_image_when_image_exists_and_force_build(
        mock_check_image_exists, docker, mock_run, caplog, config):
    mock_check_image_exists.return_value = True
    docker._force_build = True

    with caplog.at_level(logging.INFO):
        docker.build_image(config.dockerfile)

    mock_run.assert_called()
    assert "Image is already created. Using existing one." not in caplog.text
    assert "Building Docker image..." in caplog.text


@pytest.mark.parametrize("code, output, status", ((1, "", None), (0, "'running'", "'running'")))
def test_container_status(code, output, status, docker, mock_run):
    command_output = MagicMock()
    command_output.returncode = code
    command_output.stdout = output
    mock_subprocess_run.return_value = command_output
    expected_command = ["docker", "inspect", "--format='{{.State.Status}}'", docker._container_name]

    status = docker.container_status

    mock_run.assert_called_once_with(expected_command, capture_output=True, text=True)
    assert status == status


@pytest.mark.parametrize("build", (True, False))
@pytest.mark.parametrize("status", ("exited", None, "running", "dead", "created"))
@patch.object(DockerManager, "_stop_container")
@patch.object(DockerManager, "_delete_container")
@patch.object(DockerManager, "_run_container")
@patch.object(DockerManager, "_start_container")
@patch.object(DockerManager, "container_status", new_callable=PropertyMock)
def test_deploy_container(
        mock_status, mock_start, mock_run, mock_delete, mock_stop,
        status, build, docker, caplog, config
):
    container_input_directory = "/container_input_directory/"
    container_output_directory = "/container_output_directory/"
    mock_status.return_value = status
    deploy_container_args = (
        config.port,
        container_input_directory,
        container_output_directory
    )
    docker._force_build = build

    with caplog.at_level(logging.INFO):
        docker.deploy_container(*deploy_container_args)

    if status is None:
        assert "No existing container found. Running a new container." in caplog.text
        mock_start.assert_not_called()
        mock_stop.assert_not_called()
        mock_delete.assert_not_called()
        mock_run.assert_called_once_with(*deploy_container_args)
    elif build:
        assert "Force rebuild initiated." in caplog.text
        if status in ["running", "paused"]:
            mock_stop.assert_called_once()
        else:
            mock_stop.assert_not_called()
        mock_delete.assert_called_once()
        mock_run.assert_called_once_with(*deploy_container_args)
    elif status in ["exited", "created"]:
        mock_start.assert_called_once()
        mock_run.assert_not_called()
    elif status == "running":
        assert "Container is already running." in caplog.text
        mock_start.assert_not_called()
        mock_run.assert_not_called()
    else:
        assert "Container in unsupported status: dead. Fix container on your own." in caplog.text
        mock_start.assert_not_called()
        mock_run.assert_not_called()


def test_start_container_success(docker, mock_run, caplog):
    mock_subprocess_run.return_value = MagicMock()
    expected_command = ["docker", "start", docker._container_name]
    with caplog.at_level(logging.INFO):
        docker._start_container()

    mock_run.assert_called_once_with(expected_command, check=True)
    assert "Starting the existing container..." in caplog.text


def test_run_container(docker, mock_run, config, caplog):
    expected_command = [
        "docker", "run", "--name", docker._container_name, "--gpus", "all",
        "--restart", "unless-stopped", "-d",
        "-p", f"{docker._port}:{config.port}",
        "-v", f"{docker._input_directory}:{config.input_directory}",
        "-v", f"{docker._output_directory}:{config.input_directory}",
        docker._image_name
    ]
    with caplog.at_level(logging.INFO):
        docker._run_container(config.port, config.input_directory, config.input_directory)

    mock_run.assert_called_once_with(expected_command, check=True)
    assert "Running a new container..." in caplog.text


@patch.object(subprocess, "Popen", autospec=True)
def test_run_log_process(mock_popen, docker, caplog):
    command = ["docker", "logs", "-f", "--since", "1s", docker._container_name]

    with caplog.at_level(logging.INFO):
        result = docker._run_log_process()

    mock_popen.assert_called_once_with(
        command, stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT, text=True, encoding="utf-8"
    )
    assert result
    assert f"Following logs for {docker._container_name}" in caplog.text


def test_stop_container_success(docker, mock_run, caplog):
    expected_command = ["docker", "stop", docker._container_name]

    with caplog.at_level(logging.INFO):
        docker._stop_container()

    mock_run.assert_called_once_with(expected_command, check=True, capture_output=True)
    assert f"Stopping container {docker._container_name}..." in caplog.text
    assert "Container stopped." in caplog.text


def test_delete_container_success(docker, mock_run, caplog):
    expected_command = ["docker", "rm", docker._container_name]

    with caplog.at_level(logging.INFO):
        docker._delete_container()

    mock_run.assert_called_once_with(expected_command, check=True, capture_output=True)
    assert f"Deleting container {docker._container_name}..." in caplog.text
    assert "Container deleted." in caplog.text


@patch("service_manager.docker_manager.sys.stdout.write")
@patch.object(DockerManager, "_run_log_process")
@patch.object(DockerManager, "_stop_container")
def test_follow_container_logs_stopped_by_user(mock_stop, mock_run_log, mock_stdout, docker, caplog):
    mock_process = MagicMock()
    mock_process.stdout.readline.side_effect = ["log line 1\n", "log line 2\n", KeyboardInterrupt()]
    mock_run_log.return_value = mock_process
    mock_process.terminate = MagicMock()
    mock_process.wait = MagicMock()

    with caplog.at_level(logging.INFO), \
            patch.object(subprocess, "Popen", autospec=True) as pop:
        docker.follow_container_logs()

    mock_run_log.assert_called_once()
    mock_process.terminate.assert_called_once()
    mock_process.wait.assert_called_once()
    mock_stop.assert_called_once()

    calls = [call("log line 1\n"), call("log line 2\n")]
    mock_stdout.assert_has_calls(calls, any_order=True)
    assert "Process stopped by user." in caplog.text
    assert "Following container logs stopped." in caplog.text


@patch("service_manager.docker_manager.sys.stdout.write")
@patch.object(DockerManager, "_run_log_process")
@patch.object(DockerManager, "_stop_container")
def test_follow_container_logs_stopped_automatically(mock_stop, mock_run_log,
                                                     mock_stdout, docker, caplog):
    mock_process = MagicMock()
    mock_process.stdout.readline.side_effect = [
        "log line 1\n", "log line 2\n", DockerManager.ServiceShutdownSignal()
    ]
    mock_run_log.return_value = mock_process
    mock_process.terminate = MagicMock()
    mock_process.wait = MagicMock()

    with caplog.at_level(logging.INFO), \
            patch.object(subprocess, "Popen", autospec=True):
        docker.follow_container_logs()

    mock_run_log.assert_called_once()
    mock_process.terminate.assert_called_once()
    mock_process.wait.assert_called_once()
    mock_stop.assert_called_once()

    calls = [call("log line 1\n"), call("log line 2\n")]
    mock_stdout.assert_has_calls(calls, any_order=True)
    assert "Service has signaled readiness for shutdown." in caplog.text
    assert "Following container logs stopped." in caplog.text
