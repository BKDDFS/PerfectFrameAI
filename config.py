"""
Main configuration dataclass for extractor service manager tool.
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
from dataclasses import dataclass
from pathlib import Path

BASE_DIRECTORY = Path(__file__).resolve().parent


@dataclass
class Config:
    """
    Configuration settings for the extractor service management tool.

    Attributes:
        service_name (str): Name of the managing service.
        dockerfile (str): Path to the managing service dockerfile.
        port (int): Default port for the service in docker and host.
        volume_input_directory (str): Default input directory in the container.
            Note: It must be the same as default in schemas.py in service.
        volume_output_directory (str): Default output directory in the container.
            Note: It must be the same as default in schemas.py in service.
        input_directory (str): Directory with input for the extraction process.
        output_directory (str): Directory where extraction process output will be saved.
    """
    service_name: str = "extractor_service"
    dockerfile: str = str(BASE_DIRECTORY / "extractor_service")
    port: int = 8100
    volume_input_directory: str = "/app/input_directory"
    volume_output_directory: str = "/app/output_directory"
    input_directory: str = str(BASE_DIRECTORY / "input_directory")
    output_directory: str = str(BASE_DIRECTORY / "output_directory")
