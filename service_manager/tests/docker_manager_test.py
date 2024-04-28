import logging
import subprocess
from pathlib import Path
from unittest.mock import patch, MagicMock, PropertyMock, call

import pytest

from service_manager.docker_manager import DockerManager

CONTAINER_NAME = "test_container"
INPUT_DIRECTORY = Path("mock/input")
OUTPUT_DIRECTORY = Path("mock/output")
PORT = 8000
DOCKERFILE = Path("mock/dockerfile")


@pytest.fixture
def docker():
    docker = DockerManager(CONTAINER_NAME, INPUT_DIRECTORY, OUTPUT_DIRECTORY, PORT)
    return docker


def test_docker_manager_init(caplog):
    image_name = f"{CONTAINER_NAME}_image"
    expected_logs = (
        f"container_name: {CONTAINER_NAME}",
        f"image_name: {image_name}",
        f"Input directory from user: {INPUT_DIRECTORY}",
        f"Output directory from user: {OUTPUT_DIRECTORY}",
        f"Port from user: {PORT}"
    )

    with caplog.at_level(logging.DEBUG):
        docker = DockerManager(CONTAINER_NAME, INPUT_DIRECTORY, OUTPUT_DIRECTORY, PORT)

    assert docker.container_name == CONTAINER_NAME
    assert docker.image_name == image_name
    assert docker.input_directory == INPUT_DIRECTORY
    assert docker.output_directory == OUTPUT_DIRECTORY
    assert docker.port == PORT
    for message in expected_logs:
        assert message in caplog.text, \
            f"Expected phrase not found in logs: {message}"


@pytest.mark.parametrize("mock_image, is_exists", (("some_image", True), ("", False)))
@patch("service_manager.docker_manager.subprocess.run")
def test_check_image_exists(mock_run, mock_image, is_exists, docker):
    expected_command = ["docker", "images", "-q", docker.image_name]

    mock_run.return_value = MagicMock(stdout=mock_image)
    assert docker.docker_image is is_exists
    mock_run.assert_called_with(expected_command, capture_output=True, text=True)


@patch("service_manager.docker_manager.subprocess.run")
@patch("service_manager.docker_manager.DockerManager._check_image_exists")
def test_build_image(mock_check_image_exists, mock_subprocess_run, docker, caplog):
    mock_check_image_exists.return_value = False
    expected_command = ["docker", "build", "-t", docker.image_name, DOCKERFILE]

    docker.build_image(DOCKERFILE)

    mock_subprocess_run.assert_called_once_with(expected_command)


@patch("service_manager.docker_manager.subprocess.run")
@patch("service_manager.docker_manager.DockerManager._check_image_exists")
def test_build_image_when_image_exists(mock_check_image_exists, mock_subprocess_run, docker, caplog):
    mock_check_image_exists.return_value = True

    with caplog.at_level(logging.INFO):
        docker.build_image(DOCKERFILE)

    mock_subprocess_run.assert_not_called()
    assert "Image is already created. Using existing one." in caplog.text


@pytest.mark.parametrize("code, output, status", ((1, "", None), (0, "'running'", "'running'")))
@patch("service_manager.docker_manager.subprocess.run")
def test_container_status(mock_subprocess_run, code, output, status, docker):
    command_output = MagicMock()
    command_output.returncode = code
    command_output.stdout = output
    mock_subprocess_run.return_value = command_output
    expected_command = ["docker", "inspect", "--format='{{.State.Status}}'", docker.container_name]

    status = docker.container_status

    mock_subprocess_run.assert_called_once_with(expected_command, capture_output=True, text=True)
    assert status == status


@pytest.mark.parametrize(
    "status, log_message", (
        ("exited", "Starting the existing container..."),
        (None, "Container does not exist. Running a new container..."),
        ("running", "Container is already running."),
        ("dead", f"Container in unsupported status: dead. Fix container on your own.")
    )
)
@patch("service_manager.docker_manager.DockerManager._run_container")
@patch("service_manager.docker_manager.DockerManager._start_container")
@patch("service_manager.docker_manager.DockerManager.container_status", new_callable=PropertyMock)
def test_deploy_container(mock_container_status, mock_start_container,
                          mock_run_container, status, log_message, docker, caplog):
    container_input_directory = "/container_input_directory/"
    container_output_directory = "/container_output_directory/"
    mock_container_status.return_value = status
    deploy_container_args = (
        PORT,
        container_input_directory,
        container_output_directory
    )

    with caplog.at_level(logging.INFO):
        docker.deploy_container(*deploy_container_args)

    if status is None:
        mock_start_container.assert_not_called()
        mock_run_container.assert_called_once_with(*deploy_container_args)
    elif status == "exited":
        mock_start_container.assert_called_once()
        mock_run_container.assert_not_called()
    elif status == "running":
        mock_start_container.assert_not_called()
        mock_run_container.assert_not_called()
    else:
        mock_start_container.assert_not_called()
        mock_run_container.assert_not_called()
    assert log_message in caplog.text


@patch("service_manager.docker_manager.subprocess.run")
def test_start_container_success(mock_subprocess_run, docker):
    mock_subprocess_run.return_value = MagicMock()
    expected_command = ["docker", "start", docker.container_name]

    docker._start_container()

    mock_subprocess_run.assert_called_once_with(expected_command, check=True)


@patch("service_manager.docker_manager.subprocess.run")
def test_run_container(mock_subprocess_run, docker):
    input_directory = str(INPUT_DIRECTORY)
    output_directory = str(OUTPUT_DIRECTORY)
    expected_command = [
        "docker", "run", "--name", docker.container_name, "--gpus", "all",
        "--restart", "unless-stopped", "-d",
        "-p", f"{docker.port}:{PORT}",
        "-v", f"{docker.input_directory}:{input_directory}",
        "-v", f"{docker.output_directory}:{output_directory}",
        docker.image_name
    ]

    docker._run_container(PORT, input_directory, output_directory)

    mock_subprocess_run.assert_called_once_with(expected_command, check=True)


@patch.object(subprocess, "Popen", autospec=True)
def test_run_log_process(mock_popen, docker):
    command = ["docker", "logs", "-f", "--since", "1s", docker.container_name]

    result = docker._DockerManager__run_log_process()

    mock_popen.assert_called_once_with(
        command, stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT, text=True, encoding="utf-8"
    )
    assert result


@patch("service_manager.docker_manager.subprocess.run")
def test_stop_container_success(mock_subprocess_run, docker, caplog):
    mock_subprocess_run.return_value = MagicMock()
    expected_command = ["docker", "stop", docker.container_name]

    with caplog.at_level(logging.INFO):
        docker._stop_container()

    mock_subprocess_run.assert_called_once_with(expected_command, check=True, capture_output=True)
    assert f"Stopping container {docker.container_name}..." in caplog.text
    assert "Container stopped." in caplog.text


@patch("service_manager.docker_manager.subprocess.Popen")
@patch("service_manager.docker_manager.sys.stdout.write")
@patch("service_manager.docker_manager.DockerManager._DockerManager__run_log_process")
@patch("service_manager.docker_manager.DockerManager._stop_container")
def test_follow_container_logs(mock_stop_container, mock_run_log_process, mock_stdout_write, mock_popen, docker, caplog):
    mock_process = MagicMock()
    mock_process.stdout.readline.side_effect = ["log line 1\n", "log line 2\n", KeyboardInterrupt()]
    mock_run_log_process.return_value = mock_process
    mock_process.terminate = MagicMock()
    mock_process.wait = MagicMock()

    with caplog.at_level(logging.INFO):
        docker.follow_container_logs()

    mock_run_log_process.assert_called_once()
    mock_process.terminate.assert_called_once()
    mock_process.wait.assert_called_once()
    mock_stop_container.assert_called_once()

    calls = [call("log line 1\n"), call("log line 2\n")]
    mock_stdout_write.assert_has_calls(calls, any_order=True)

    assert f"Following logs for {docker.container_name}" in caplog.text
    assert "Process stopped by user." in caplog.text
