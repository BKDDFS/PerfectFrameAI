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
import os
import sys

import uvicorn
from fastapi import BackgroundTasks, Depends, FastAPI

if os.getenv("DOCKER_ENV"):
    from app.dependencies import (ExtractorDependencies,
                                  get_extractor_dependencies)
    from app.extractor_manager import ExtractorManager
    from app.schemas import ExtractorConfig, ExtractorStatus, Message
else:
    from .app.dependencies import (ExtractorDependencies,
                                   get_extractor_dependencies)
    from .app.extractor_manager import ExtractorManager
    from .app.schemas import ExtractorConfig, ExtractorStatus, Message

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S",
                    handlers=[logging.StreamHandler(sys.stdout)])
logger = logging.getLogger(__name__)

app = FastAPI()


@app.get("/v2/status")
def get_extractors_status() -> ExtractorStatus:
    """
    Checks is some extractor already running on service.

    Returns:
        ExtractorStatus: Contains the name of the currently active extractor.
    """
    return ExtractorStatus(active_extractor=ExtractorManager.get_active_extractor())


@app.post("/v2/extractors/{extractor_name}")
def run_extractor(
        extractor_name: str,
        background_tasks: BackgroundTasks,
        config: ExtractorConfig = ExtractorConfig(),
        dependencies: ExtractorDependencies = Depends(get_extractor_dependencies)
) -> Message:
    """
    Runs provided extractor.

    Args:
        extractor_name (str): The name of the extractor that will be used.
        background_tasks (BackgroundTasks): A FastAPI tool for running tasks in background.
        dependencies(ExtractorDependencies): Dependencies that will be used in extractor.
        config (ExtractorConfig): A Pydantic model with extractor configuration.

    Returns:
        Message: Contains the operation status.
    """
    message = ExtractorManager.start_extractor(extractor_name, background_tasks,
                                               config, dependencies)
    return Message(message=message)


if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=8100, reload=True)
