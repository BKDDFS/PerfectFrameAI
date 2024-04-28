"""
This module provide script for starting extraction process with
given arguments in fast and easy way.
"""
import logging
import argparse

from config import Config
from service_manager.docker_manager import DockerManager
from service_manager.service_initializer import ServiceInitializer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main() -> None:
    """Script for starting extractor service and extraction process."""
    user_input = parse_args()
    service = ServiceInitializer(user_input)
    docker = DockerManager(
        Config.service_name,
        user_input.input_dir,
        user_input.output_dir,
        user_input.port
    )
    docker.build_image(Config.dockerfile_path)
    docker.deploy_container(
        Config.default_port,
        Config.volume_input_directory,
        Config.volume_output_directory
    )
    service.run_extractor()
    docker.follow_container_logs()


def parse_args() -> argparse.Namespace:
    """
    Parses command line arguments from user for extractor service.

    Returns:
        argparse.Namespace: Arguments from user.
    """
    parser = argparse.ArgumentParser(
        description="Tool to manage and execute image processing tasks within a Docker container."
    )
    parser.add_argument("extractor_name",
                        choices=["best_frames_extractor", "top_images_extractor"],
                        help="Name of extractor to run.")
    parser.add_argument("--input_dir", "-i", default=Config.default_input_directory,
                        help="Full path to the extractors input directory.")
    parser.add_argument("--output_dir", "-o", default=Config.default_output_directory,
                        help="Full path to the extractors output directory.")
    parser.add_argument("--port", "-p", type=int, default=Config.default_port,
                        help="Port to expose the service on the host.")
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    main()
