"""This module provide tool for starting extractor service."""
import argparse
import json
import logging
import time
from pathlib import Path
from typing import Union
from urllib.request import urlopen, Request
from http.client import RemoteDisconnected

logger = logging.getLogger(__name__)


class ServiceInitializer:
    """
    Handles command-line input and manages the setup and
    execution of Docker-based image processing tasks.
    """
    def __init__(self, user_input: argparse.Namespace) -> None:
        """Initializes the service initializer by taking and validating user input."""
        self.input_directory = self._check_directory(user_input.input_dir)
        self.output_directory = self._check_directory(user_input.output_dir)
        self.extractor_name = user_input.extractor_name
        self.port = user_input.port

    @staticmethod
    def _check_directory(directory: str) -> Path:
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

    def run_extractor(self, extractor_url: Union[str, None] = None) -> None:
        """Send POST request to local port extractor service to start chosen extractor."""
        if not extractor_url:
            extractor_url = f"http://localhost:{self.port}/extractors/{self.extractor_name}"
        req = Request(extractor_url, method="POST")
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
                    response_body = json.loads(response_body.decode("utf-8"))
                    message = response_body.get("message", "No message returned")
                    logger.info("Response from server: %s", message)
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
