"""
This module provide script for starting extraction process with
given arguments in fast and easy way.
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
        user_input.port,
        user_input.build
    )
    docker.build_image(Config.dockerfile)
    docker.deploy_container(
        Config.port,
        Config.volume_input_directory,
        Config.volume_output_directory
    )
    service.run_extractor()
    docker.follow_container_logs()
    logger.info("Process stopped.")


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
    parser.add_argument("--input_dir", "-i", default=Config.input_directory,
                        help="Full path to the extractors input directory.")
    parser.add_argument("--output_dir", "-o", default=Config.output_directory,
                        help="Full path to the extractors output directory.")
    parser.add_argument("--port", "-p", type=int, default=Config.port,
                        help="Port to expose the service on the host.")
    parser.add_argument("--build", "-b", action="store_true",
                        help="Forces the Docker image to be rebuilt if set to true.")
    parser.add_argument("--all_frames", action="store_true",
                        help="Returning all frames every second without filtering. "
                             "For best_frames_extractor - does nothing with others.")
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    main()
