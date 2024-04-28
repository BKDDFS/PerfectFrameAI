"""Main configuration dataclass for extractor service manage tool."""
from dataclasses import dataclass
from pathlib import Path

current_directory = Path.cwd()


@dataclass
class Config:
    """
    Configuration settings for the extractor service management tool.

    Attributes:
        service_name (str): Name of the managing service.
        dockerfile_path (str): Path to the managing service dockerfile.
        default_port (int): Default port for the service in docker and host.
        volume_input_directory (str): Default input directory in the container.
            Note: It must be the same as default in schemas.py in service.
        volume_output_directory (str): Default output directory in the container.
            Note: It must be the same as default in schemas.py in service.
        default_input_directory (str): Directory with input for the extraction process.
        default_output_directory (str): Directory where extraction process output will be saved.
    """
    service_name: str = "extractor_service"
    dockerfile_path: str = str(current_directory / "extractor_service")
    default_port: int = 8100
    volume_input_directory: str = "/app/input_directory"
    volume_output_directory: str = "/app/output_directory"
    default_input_directory: str = str(current_directory / "input_directory")
    default_output_directory: str = str(current_directory / "output_directory")
