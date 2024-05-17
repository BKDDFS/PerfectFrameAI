"""
This module defines a FastAPI web application for managing image extractors.

Endpoints:
    GET /status:
        For checking is some extractor already running.
    POST /extractors/{extractor_name}:
        For running chosen extractor.
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
import sys

import uvicorn
from fastapi import FastAPI, BackgroundTasks

from app.schemas import ExtractorConfig, Message, ExtractorStatus
from app.extractor_manager import ExtractorManager

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    handlers=[logging.StreamHandler(sys.stdout)])
logger = logging.getLogger(__name__)

app = FastAPI()


@app.get("/status")
def get_extractors_status() -> ExtractorStatus:
    """
    Checks is some extractor already running on service.

    Returns:
        ExtractorStatus: Contains the name of the currently active extractor.
    """
    return ExtractorStatus(active_extractor=ExtractorManager.get_active_extractor())


@app.post("/extractors/{extractor_name}")
def run_extractor(background_tasks: BackgroundTasks, extractor_name: str,
                  config: ExtractorConfig = ExtractorConfig()) -> Message:
    """
    Runs provided extractor.

    Args:
        background_tasks (BackgroundTasks): A FastAPI tool for running tasks in background,
            which allows non-blocking operation of long-running tasks.
        extractor_name (str): The name of the extractor that will be used.
        config (ExtractorConfig): A Pydantic model with configuration
            parameters for the extractor.

    Returns:
        Message: Contains the operation status.
    """
    message = ExtractorManager.start_extractor(background_tasks, config, extractor_name)
    return Message(message=message)


if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=8100, reload=True)
