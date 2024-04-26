"""Ze względu na to, że instalowanie zależności do czegoś
co ma zautomatyzować instalowanie zależności jest bez sensu,
zdecydowałem się, że napiszę własny manager do obsługi dockera.
"""
import subprocess
import sys
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class DockerManager:
    def __init__(self, container_name: str, input_dir: Path, output_dir: Path, port: int) -> None:
        self.container_name = container_name
        self.image_name = f"{self.container_name}_image"
        self.input_directory = input_dir
        self.output_directory = output_dir
        self.port = port
        self.__log_input()

    def __log_input(self):
        """Log user input if debugging."""
        logger.debug("container_name: %s", self.container_name)
        logger.debug("image_name: %s", self.image_name)
        logger.debug("Input directory from user: %s", self.input_directory)
        logger.debug("Output directory from user: %s", self.output_directory)
        logger.debug("Port from user: %s", self.port)

    @property
    def docker_image(self):
        return self._check_image_exists()

    def _check_image_exists(self) -> bool:
        """Check if the Docker image exists."""
        command = ["docker", "images", "-q", self.image_name]
        process_output = subprocess.run(command, capture_output=True, text=True).stdout.strip()
        is_exists = process_output != ""
        return is_exists

    def build_image(self, dockerfile_path):
        """Builds a Docker image from a Dockerfile located in a subdirectory."""
        if not self.docker_image:
            logging.info("Building Docker image...")
            command = ["docker", "build", "-t", self.image_name, dockerfile_path]
            subprocess.run(command)
        else:
            logger.info("Image is already created. Using existing one.")

    @property
    def container_status(self) -> str:
        return self._check_container_status()

    def _check_container_status(self) -> str:
        """Check the status of the container."""
        command = ["docker", "inspect", "--format='{{.State.Status}}'", self.container_name]
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.strip().replace('"', '')

    def deploy_container(self, container_port: int, container_input_directory: str, container_output_directory: str):
        """Decide whether to start or run the container based on its current status."""
        status = self.container_status
        if status is None:
            logging.info("Container does not exist. Running a new container...")
            self._run_container(container_port, container_input_directory, container_output_directory)
        elif status == "'exited'":
            logging.info("Starting the existing container...")
            self._start_container()
        elif status == "'running'":
            logging.info(f"Container is already running.")
        else:
            logging.warning(f"Container in unsupported status: %s. Fix container on your own.", status)

    def _start_container(self) -> None:
        """Start the container if it exists but stopped."""
        command = ["docker", "start", self.container_name]
        subprocess.run(command, check=True)

    def _run_container(self, container_port: int, container_input_directory: str,
                       container_output_directory: str) -> None:
        """Deploy the container if it does not exist."""
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
        """Follows logs from the running Docker container starting
        from the moment this method is called.
        """
        logger.info(f"Following logs for {self.container_name}...")
        process = self.__run_log_process()
        try:
            for line in iter(process.stdout.readline, ''):
                sys.stdout.write(line)
        except KeyboardInterrupt:
            logger.info("Process stopped by user.")
        finally:
            self.__stop_log_process(process)

    def __run_log_process(self) -> subprocess.Popen:
        command = ["docker", "logs", "-f", "--since", "1s", self.container_name]
        process = subprocess.Popen(
            command, stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT, text=True, encoding="utf-8"
        )
        return process

    def __stop_log_process(self, process: subprocess.Popen) -> None:
        process.terminate()
        process.wait()
        self._stop_container()

    def _stop_container(self) -> None:
        """Stops the running Docker container."""
        logger.info(f"Stopping container %s...", self.container_name)
        command = ["docker", "stop", self.container_name]
        subprocess.run(command, check=True, capture_output=True)
        logger.info("Container stopped.")
