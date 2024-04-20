import http
import logging
import argparse
import time
import urllib.error
from pathlib import Path
from urllib import request

import config
from docker_manager import DockerManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Setup:
    def __init__(self) -> None:
        args = self.__parse_args()
        self.extractor_name = args.extractor_name
        self.input_directory = args.input
        self.output_directory = args.output
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
        if not Path(args.input).is_dir():
            error_massage = f"Invalid directory path: {args.input}"
            logger.error(error_massage)
            raise NotADirectoryError(error_massage)
        elif not Path(args.output).is_dir():
            error_massage = f"Invalid directory path: {args.input}"
            logger.error(error_massage)
            raise NotADirectoryError(error_massage)
        return args

    def run_extractor(self) -> None:
        start_time = time.time()
        url = f"http://localhost:{self.port}/extractors/{self.extractor_name}"
        req = urllib.request.Request(url, method="POST")
        while True:
            extraction_started = self.__try_to_run_extractor(req, start_time)
            if extraction_started:
                break

    @staticmethod
    def __try_to_run_extractor(req, start_time, timeout=60) -> bool:
        try:
            with urllib.request.urlopen(req) as response:
                if response.status == 200:
                    response_body = response.read()
                    print("Response from server:", response_body)
                    return True
        except urllib.error.URLError:
            print("Waiting for service to be available...")
            time.sleep(3)
        except http.client.RemoteDisconnected:
            print("Remote end closed connection, retrying...")
            time.sleep(3)
        if time.time() - start_time > timeout:
            raise TimeoutError("Timed out waiting for service to respond")
        return False


if __name__ == "__main__":
    setup = Setup()
    docker = DockerManager(
        config.service_name, setup.input_directory,
        setup.output_directory, setup.port
    )
    docker.build_image()
    docker.remove_container()
    docker.run_container()
    setup.run_extractor()
    docker.follow_logs()
