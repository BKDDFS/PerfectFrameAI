"""
Main configuration file for extractor service manage tool.

Attributes:
    service_name (str): Name of the managing service.
    dockerfile_path (str): Managing service dockerfile path.
    default_port (int): Default port for service in docker and host.
    volume_input_directory (str): Default input directory in container.
        Note: It must be same as default in schemas.py in service.
    volume_output_directory (str): Default input directory in container.
        Note: It must be same as default in schemas.py in service.
    default_input_directory: Directory with input for extraction process.
    default_output_directory: Directory where extraction process output will be saved.
"""
from pathlib import Path

current_directory = Path.cwd()

service_name = "extractor_service"
dockerfile_path = str(current_directory / "extractor_service")
default_port = 8100
volume_input_directory = "/app/input_directory"
volume_output_directory = "/app/output_directory"
default_input_directory = str(current_directory / "input_directory")
default_output_directory = str(current_directory / "output_directory")
