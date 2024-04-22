import subprocess
import sys
from pathlib import Path
import logging

import config

logger = logging.getLogger(__name__)


class DockerManager:
    def __init__(self, input_dir: Path, output_dir: Path, port: int) -> None:
        self.container_name = config.service_name
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

    def _check_image_exists(self) -> bool:
        """Check if the Docker image exists."""
        command = ['docker', 'images', '-q', self.image_name]
        process_output = subprocess.run(command, capture_output=True, text=True).stdout.strip()
        is_exists = process_output != ""
        return is_exists

    def build_image(self):
        """Builds a Docker image from a Dockerfile located in a subdirectory."""
        if not self._check_image_exists():
            logging.info("Building Docker image...")
            command = ['docker', 'build', '-t', self.image_name, config.dockerfile_path]
            subprocess.run(command)
        else:
            logger.info("Image is already created. Using existing one.")

    def _container_status(self):
        """Check the status of the container."""
        command = ['docker', 'inspect', '--format="{{.State.Status}}"', self.container_name]
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.strip().replace('"', '')
        return None

    def deploy_container(self):
        """Decide whether to start or run the container based on its current status."""
        status = self._container_status()
        if status == 'exited':
            logging.info("Starting the existing container...")
            self._start_container()
        elif status is None:
            logging.info("Container does not exist. Running a new container...")
            self._run_container()
        else:
            logging.info(f"Container is already {status}.")

    def _start_container(self):
        """Start the container if it exists but stopped."""
        command = ['docker', 'start', self.container_name]
        subprocess.run(command, check=True)

    def _run_container(self):
        """Deploy the container if it does not exist."""
        logger.info(f"Running container %s...", self.container_name)
        command = [
            'docker', 'run', '--name', self.container_name, '--gpus', 'all',
            '--restart', 'unless-stopped', '-d',
            '-p', f'{self.port}:{config.default_port}',
            '-v', f'{self.input_directory}:{config.service_default_input_directory}',
            '-v', f'{self.output_directory}:{config.service_default_output_directory}',
            self.image_name
        ]
        subprocess.run(command, check=True)

    def follow_logs(self):
        """Follows logs from the running Docker container starting
        from the moment this method is called.
        """
        logger.info(f"Following logs for {self.container_name}...")
        command = ['docker', 'logs', '-f', '--since', '1s', self.container_name]
        process = subprocess.Popen(
            command, stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT, text=True, encoding="utf-8"
        )
        try:
            for line in iter(process.stdout.readline, ''):
                sys.stdout.write(line)
        except KeyboardInterrupt:
            logger.info("Process stopped by user.")
        finally:
            process.terminate()
            process.wait()
            self.__stop_container()

    def __stop_container(self):
        """Stops the running Docker container."""
        logger.info(f"Stopping container %s...", self.container_name)
        command = ['docker', 'stop', self.container_name]
        subprocess.run(command, check=True, capture_output=True)
        logger.info("Container stopped.")
