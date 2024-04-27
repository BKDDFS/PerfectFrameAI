"""

"""
import logging
import argparse
import time
from pathlib import Path
from urllib.request import urlopen, Request
from http.client import RemoteDisconnected

import config
from docker_manager import DockerManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def check_directory(directory: str) -> Path:
    """
    Validates if the provided directory path is an actual directory.

    Args:
        directory (str): The directory path to validate.

    Returns:
        Path: The validated directory as a Path object.

    Raises:
        NotADirectoryError: If the provided path is not a directory.
    """
    directory = Path(directory)
    if not directory.is_dir():
        error_massage = f"Invalid directory path: {str(directory)}"
        logger.error(error_massage)
        raise NotADirectoryError(error_massage)
    return directory


class Setup:
    """
    Handles command-line input and manages the setup and
    execution of Docker-based image processing tasks.
    """
    def __init__(self) -> None:
        """Initializes the setup by parsing and validating command line arguments."""
        args = self.__parse_args()
        self.input_directory = check_directory(args.input)
        self.output_directory = check_directory(args.output)
        self.extractor_name = args.extractor_name
        self.port = args.port

    @staticmethod
    def __parse_args() -> argparse.Namespace:
        """
        Parses command line arguments.

        Returns:
            argparse.Namespace: The namespace populated with command line arguments.
        """
        parser = argparse.ArgumentParser(description="Manage Docker container for image processing.")
        parser.add_argument("extractor_name",
                            choices=['best_frames_extractor', 'top_images_extractor'],
                            help="Name of extractor to run.")
        parser.add_argument("--input", "-i", default=config.default_input_directory,
                            help="Full path to the input directory")
        parser.add_argument("--output", "-o", default=config.default_output_directory,
                            help="Full path to the output directory")
        parser.add_argument("--port", "-p", type=int, default=config.default_port,
                            help="Port to expose the service on the host")
        args = parser.parse_args()
        return args

    def run_extractor(self) -> None:
        """Send POST request to local port extractor service to start chosen extractor."""
        url = f"http://localhost:{self.port}/extractors/{self.extractor_name}"
        req = Request(url, method="POST")
        start_time = time.time()
        while True:
            if self._try_to_run_extractor(req, start_time):
                break

    def _try_to_run_extractor(self, req: Request, start_time: float, timeout: int = 60) -> bool:
        """
        Attempts to send a request to the extractor service
        and handles service availability and timeouts.

        Args:
            req (Request): The request object to send.
            start_time (float): The timestamp at the start of the operation for timeout management.
            timeout (int): Maximum time in seconds to wait for the service to become available.

        Returns:
            bool: True if the service response as expected, False otherwise.
        """
        try:
            with urlopen(req) as response:
                if response.status == 200:
                    response_body = response.read()
                    logger.info("Response from server: %s", response_body)
                    return True
        except RemoteDisconnected:
            logger.info("Waiting for service to be available...")
            self.__check_timeout(start_time, timeout)
            time.sleep(3)
        return False

    @staticmethod
    def __check_timeout(start_time: float, timeout: int) -> None:
        """
        Checks if the operation has timed out based on the start time and specified timeout.

        Args:
            start_time (float): The start time of the operation.
            timeout (int): The maximum allowable duration for the operation.

        Raises:
            TimeoutError: If the current time exceeds the start time by the timeout duration.
        """
        if time.time() - start_time > timeout:
            error_massage = "Timed out waiting for service to respond."
            logger.error(error_massage)
            raise TimeoutError(error_massage)


if __name__ == "__main__":
    setup = Setup()
    docker = DockerManager(
        config.service_name,
        setup.input_directory,
        setup.output_directory,
        setup.port
    )
    docker.build_image(config.dockerfile_path)
    docker.deploy_container(
        config.default_port,
        config.default_container_input_directory,
        config.default_container_output_directory
    )
    setup.run_extractor()
    docker.follow_container_logs()
