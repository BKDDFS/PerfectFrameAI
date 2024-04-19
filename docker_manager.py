import subprocess
from pathlib import Path
import logging

import config

logger = logging.getLogger(__name__)


class DockerManager:
    def __init__(self, container_name, input_dir, output_dir, port=8100):
        self.container_name = container_name
        self.image_name = f"{container_name}_image"
        self.input_dir = Path(input_dir).resolve()
        self.output_dir = Path(output_dir).resolve()
        self.port = port

    def build_image(self):
        """Builds a Docker image from a Dockerfile located in a subdirectory."""
        logging.info("Building Docker image...")
        command = ['docker', 'build', '-t', self.image_name, config.dockerfile_path]
        self.run_command(command)

    def remove_container(self):
        """Removes an existing container with the same name if it exists."""
        logging.info(f"Removing existing container %s...", self.container_name)
        command = ['docker', 'rm', '-f', self.container_name]
        self.run_command(command, silent=True)

    def run_container(self):
        """Runs a Docker container with mounted volumes and specified port."""
        logger.info(f"Running container %s...", self.container_name)
        command = [
            'docker', 'run', '--name', self.container_name, '--gpus', 'all',
            '-p', f'{self.port}:{config.default_port}',
            '-v', f'{self.input_dir}:{config.service_default_input_directory}',
            '-v', f'{self.output_dir}:{config.service_default_output_directory}',
            '-d',
            self.image_name
        ]
        self.run_command(command, silent=True)
        # process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        # self.stream_output(process)

    @staticmethod
    def stream_output(process: subprocess):
        """Streams output from the Docker container and handles process termination."""
        try:
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    print(output.strip())
            stderr = process.stderr.read()
            if stderr:
                print('STDERR:', stderr.strip())
        finally:
            process.terminate()

    @staticmethod
    def run_command(command, silent=False):
        """Executes a shell command."""
        if silent:
            subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            subprocess.run(command, check=True)
