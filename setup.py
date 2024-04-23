import logging
import argparse
import time
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import URLError
from http.client import RemoteDisconnected

import config
from docker_manager import DockerManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Setup:
    def __init__(self) -> None:
        args = self.__parse_args()
        self.input_directory = self.__check_directory(args.input)
        self.output_directory = self.__check_directory(args.output)
        self.extractor_name = args.extractor_name
        self.port = args.port

    @staticmethod
    def __parse_args() -> argparse.Namespace:
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

    @staticmethod
    def __check_directory(directory: str) -> Path:
        directory = Path(directory)
        if not directory.is_dir():
            error_massage = f"Invalid directory path: {directory}"
            logger.error(error_massage)
            raise NotADirectoryError(error_massage)
        return directory

    def run_extractor(self) -> None:
        start_time = time.time()
        url = f"http://localhost:{self.port}/extractors/{self.extractor_name}"
        req = Request(url, method="POST")
        while True:
            if self._try_to_run_extractor(req, start_time):
                break

    @staticmethod
    def _try_to_run_extractor(req, start_time, timeout=60) -> bool:
        try:
            with urlopen(req) as response:
                if response.status == 200:
                    response_body = response.read()
                    print("Response from server:", response_body)
                    return True
        except RemoteDisconnected:
            print("Waiting for service to be available...")
            time.sleep(3)
        if time.time() - start_time > timeout:
            raise TimeoutError("Timed out waiting for service to respond.")
        return False


if __name__ == "__main__":
    setup = Setup()
    docker = DockerManager(
        setup.input_directory,
        setup.output_directory,
        setup.port
    )
    docker.build_image()
    docker.deploy_container()
    setup.run_extractor()
    docker.follow_logs()
