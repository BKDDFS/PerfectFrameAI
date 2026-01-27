"""Define a FastAPI web application for managing image extractors.

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
from typing import Annotated

from fastapi import BackgroundTasks, Depends, FastAPI

from perfectframe.dependencies import ExtractorDependencies, get_extractor_dependencies
from perfectframe.extractor_manager import ExtractorManager
from perfectframe.schemas import ExtractorConfig, ExtractorName, ExtractorStatus, Message

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

app = FastAPI()


@app.get("/health")
def health_check() -> dict[str, str]:
    """Health check endpoint for container health monitoring."""
    return {"status": "healthy"}


@app.get("/v2/status")
def get_extractors_status() -> ExtractorStatus:
    """Check if some extractor is already running on service."""
    return ExtractorStatus(active_extractor=ExtractorManager.get_active_extractor())


@app.post("/v2/extractors/{extractor_name}")
def run_extractor(
    extractor_name: ExtractorName,
    background_tasks: BackgroundTasks,
    dependencies: Annotated[ExtractorDependencies, Depends(get_extractor_dependencies)],
    config: ExtractorConfig = ExtractorConfig(),
) -> Message:
    """Run the provided extractor."""
    message = ExtractorManager.start_extractor(
        extractor_name, background_tasks, config, dependencies
    )
    return Message(message=message)
