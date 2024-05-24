"""
I built a custom Docker manager because I wanted to simplify and accelerate the process of
launching the service using a script as much as possible. Therefore,
I didn’t want to use any external libraries in this part of the project.

This module defines a DockerManager class to handle Docker operations like building images,
managing container lifecycle, and monitoring container logs.
LICENSE
=======
Copyright (C) 2024  Bartłomiej Flis

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
import subprocess
import sys
import logging

logger = logging.getLogger(__name__)


class DockerManager:
    """
    Manages Docker containers and images, including operations like building, starting,
    stopping, and logging containers.
    """
    class ServiceShutdownSignal(Exception):
        """Exception raised when the service signals it is ready to be shut down."""

    def __init__(self, container_name: str, input_dir: str,
                 output_dir: str, port: int, force_build: bool) -> None:
        """
        Initialize the DockerManager with specific parameters for container and image management.

        Args:
            container_name (str): Name of the Docker container.
            input_dir (str): Path to the directory for input data volumes.
            output_dir (str): Path to the directory for output data volumes.
            port (int): Port number to expose from the container.
        """
        self._container_name = container_name
        self._image_name = f"{self._container_name}_image"
        self._input_directory = input_dir
        self._output_directory = output_dir
        self._port = port
        self._force_build = force_build
        self.__log_input()

    @property
    def image_name(self):
        return self._image_name

    def __log_input(self) -> None:
        """Log user input if debugging."""
        logger.debug("container_name: %s", self._container_name)
        logger.debug("image_name: %s", self._image_name)
        logger.debug("Input directory from user: %s", self._input_directory)
        logger.debug("Output directory from user: %s", self._output_directory)
        logger.debug("Port from user: %s", self._port)
        logger.debug("Force build: %s", self._force_build)

    @property
    def docker_image_existence(self) -> bool:
        return self._check_image_exists()

    def _check_image_exists(self) -> bool:
        """Checks whether the Docker image already exists in the system.

        Returns:
            bool: True if the image exists, False otherwise.
        """
        command = ["docker", "images", "-q", self._image_name]
        process_output = subprocess.run(command, capture_output=True, text=True).stdout.strip()
        is_exists = process_output != ""
        return is_exists

    def build_image(self, dockerfile_path: str) -> None:
        """
        Builds a Docker image from a Dockerfile located in a subdirectory.

        Args:
            dockerfile_path (str): Path to the Dockerfile.
        """
        if not self.docker_image_existence or self._force_build:
            logging.info("Building Docker image...")
            command = ["docker", "build", "-t", self._image_name, dockerfile_path]
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
        command = ["docker", "inspect", "--format='{{.State.Status}}'", self._container_name]
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
            logging.info("No existing container found. Running a new container.")
            self._run_container(container_port, container_input_directory, container_output_directory)
        elif self._force_build:
            logging.info("Force rebuild initiated.")
            if status in ["running", "paused"]:
                self._stop_container()
            self._delete_container()
            self._run_container(container_port, container_input_directory, container_output_directory)
        elif status in ["exited", "created"]:
            self._start_container()
        elif status == "running":
            logging.info(f"Container is already running.")
        else:
            logging.warning(f"Container in unsupported status: %s. Fix container on your own.",
                            status)

    def _start_container(self) -> None:
        """Start the container if it exists but stopped."""
        logging.info("Starting the existing container...")
        command = ["docker", "start", self._container_name]
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
        logging.info("Running a new container...")
        command = [
            "docker", "run", "--name", self._container_name, "--gpus", "all",
            "--restart", "unless-stopped", "-d",
            "-p", f"{self._port}:{container_port}",
            "-v", f"{self._input_directory}:{container_input_directory}",
            "-v", f"{self._output_directory}:{container_output_directory}",
            self._image_name
        ]
        subprocess.run(command, check=True)

    def follow_container_logs(self) -> None:
        """Starts following the logs of the running Docker container."""
        try:
            process = self._run_log_process()
            for line in iter(process.stdout.readline, ''):
                sys.stdout.write(line)
                if "Service ready for shutdown" in line:
                    raise self.ServiceShutdownSignal("Service has signaled readiness for shutdown.")
        except KeyboardInterrupt:
            logger.info("Process stopped by user.")
        except self.ServiceShutdownSignal:
            logger.info("Service has signaled readiness for shutdown.")
        finally:
            self.__stop_log_process(process)

    def _run_log_process(self) -> subprocess.Popen:
        """Initiates the process to follow Docker container logs.

        Returns:
            subprocess.Popen: The process object for the log following command.
        """
        logger.info(f"Following logs for {self._container_name}...")
        command = ["docker", "logs", "-f", "--since", "1s", self._container_name]
        process = subprocess.Popen(
            command, stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT, text=True, encoding="utf-8"
        )
        return process

    def __stop_log_process(self, process: subprocess.Popen) -> None:
        """Terminates the log following process and stops the container.

        Args:
            process (subprocess.Popen): The process object for the log following command.
        """
        logger.info("Following container logs stopped.")
        process.terminate()
        process.wait()
        self._stop_container()

    def _stop_container(self) -> None:
        """Stops the running Docker container."""
        logger.info(f"Stopping container %s...", self._container_name)
        command = ["docker", "stop", self._container_name]
        subprocess.run(command, check=True, capture_output=True)
        logger.info("Container stopped.")

    def _delete_container(self) -> None:
        """Deletes the Docker container."""
        logger.info(f"Deleting container %s...", self._container_name)
        command = ["docker", "rm", self._container_name]
        subprocess.run(command, check=True, capture_output=True)
        logger.info("Container deleted.")
