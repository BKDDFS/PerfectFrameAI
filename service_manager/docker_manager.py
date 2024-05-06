"""
I built a custom Docker manager because I wanted to simplify and accelerate the process of
launching the service using a script as much as possible. Therefore,
I didn’t want to use any external libraries in this part of the project.

This module defines a DockerManager class to handle Docker operations like building images,
managing container lifecycle, and monitoring container logs.
"""
import signal
import subprocess
import sys
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class ServiceShutdownSignal(Exception):
    """Exception raised when the service signals it is ready to be shut down."""


class DockerManager:
    """
    Manages Docker containers and images, including operations like building, starting,
    stopping, and logging containers.
    """

    def __init__(self, container_name: str, input_dir: Path, output_dir: Path, port: int) -> None:
        """
        Initialize the DockerManager with specific parameters for container and image management.

        Args:
            container_name (str): Name of the Docker container.
            input_dir (Path): Path to the directory for input data volumes.
            output_dir (Path): Path to the directory for output data volumes.
            port (int): Port number to expose from the container.
        """
        self.container_name = container_name
        self.image_name = f"{self.container_name}_image"
        self.input_directory = input_dir
        self.output_directory = output_dir
        self.port = port
        self.__log_input()

    def __log_input(self) -> None:
        """Log user input if debugging."""
        logger.debug("container_name: %s", self.container_name)
        logger.debug("image_name: %s", self.image_name)
        logger.debug("Input directory from user: %s", self.input_directory)
        logger.debug("Output directory from user: %s", self.output_directory)
        logger.debug("Port from user: %s", self.port)

    @property
    def docker_image(self) -> bool:
        return self._check_image_exists()

    def _check_image_exists(self) -> bool:
        """Checks whether the Docker image already exists in the system.

        Returns:
            bool: True if the image exists, False otherwise.
        """
        command = ["docker", "images", "-q", self.image_name]
        process_output = subprocess.run(command, capture_output=True, text=True).stdout.strip()
        is_exists = process_output != ""
        return is_exists

    def build_image(self, dockerfile_path) -> None:
        """
        Builds a Docker image from a Dockerfile located in a subdirectory.

        Args:
            dockerfile_path: Path to the Dockerfile.
        """
        if not self.docker_image:
            logging.info("Building Docker image...")
            command = ["docker", "build", "-t", self.image_name, dockerfile_path]
            subprocess.run(command)
        else:
            logger.info("Image is already created. Using existing one.")

    @property
    def container_status(self) -> str:
        """
        Retrieves the current status of the Docker container.

        Returns:
            str: Container status.
        """
        return self._check_container_status()

    def _check_container_status(self) -> str:
        """
        Check the status of the container.

        Returns:
            str: The status of the container.
        """
        command = ["docker", "inspect", "--format='{{.State.Status}}'", self.container_name]
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.strip().replace("'", "")

    def deploy_container(self, container_port: int, container_input_directory: str,
                         container_output_directory: str) -> None:
        """Deploys or starts the Docker container based on its current status.

        Args:
            container_port (int): Port to expose on the Docker container.
            container_input_directory (str): Directory inside the container for input data.
            container_output_directory (str): Directory inside the container for output data.
        """
        status = self.container_status
        if status is None:
            logging.info("Container does not exist. Running a new container...")
            self._run_container(container_port, container_input_directory, container_output_directory)
        elif status == "exited":
            logging.info("Starting the existing container...")
            self._start_container()
        elif status == "running":
            logging.info(f"Container is already running.")
        else:
            logging.warning(f"Container in unsupported status: %s. Fix container on your own.",
                            status)

    def _start_container(self) -> None:
        """Start the container if it exists but stopped."""
        command = ["docker", "start", self.container_name]
        subprocess.run(command, check=True)

    def _run_container(self, container_port: int, container_input_directory: str,
                       container_output_directory: str) -> None:
        """
        Runs a new Docker container using the configured parameters.

        Args:
            container_port (int): Port to expose on the Docker container.
            container_input_directory (str): Directory inside the container for input data.
            container_output_directory (str): Directory inside the container for output data.
        """
        command = [
            "docker", "run", "--name", self.container_name, "--gpus", "all",
            "--restart", "unless-stopped", "-d",
            "-p", f"{self.port}:{container_port}",
            "-v", f"{self.input_directory}:{container_input_directory}",
            "-v", f"{self.output_directory}:{container_output_directory}",
            self.image_name
        ]
        subprocess.run(command, check=True)

    def follow_container_logs(self) -> None:
        """Starts following the logs of the running Docker container."""
        try:
            logger.info(f"Following logs for {self.container_name}...")
            process = self._run_log_process()
            for line in iter(process.stdout.readline, ''):
                sys.stdout.write(line)
                if "Service ready for shutdown" in line:
                    raise ServiceShutdownSignal("Service has signaled readiness for shutdown.")
        except KeyboardInterrupt:
            logger.info("Process stopped by user.")
        except ServiceShutdownSignal:
            logger.info("Service has signaled readiness for shutdown.")
        finally:
            self._stop_log_process(process)

    def handle_sigusr1(self, _, __):
        raise ServiceShutdownSignal("Service has signaled readiness for shutdown.")

    def _run_log_process(self) -> subprocess.Popen:
        """Initiates the process to follow Docker container logs.

        Returns:
            subprocess.Popen: The process object for the log following command.
        """
        command = ["docker", "logs", "-f", "--since", "1s", self.container_name]
        process = subprocess.Popen(
            command, stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT, text=True, encoding="utf-8"
        )
        return process

    def _stop_log_process(self, process: subprocess.Popen) -> None:
        """Terminates the log following process and stops the container.

        Args:
            process (subprocess.Popen): The process object for the log following command.
        """
        process.terminate()
        process.wait()
        self._stop_container()

    def _stop_container(self) -> None:
        """Stops the running Docker container."""
        logger.info(f"Stopping container %s...", self.container_name)
        command = ["docker", "stop", self.container_name]
        subprocess.run(command, check=True, capture_output=True)
        logger.info("Container stopped.")
