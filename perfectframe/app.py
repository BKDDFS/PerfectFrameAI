"""Define a FastAPI web application for managing image extractors."""

import logging
import sys
from typing import Annotated

from fastapi import BackgroundTasks, Depends, FastAPI

from perfectframe.dependencies import Dependencies, get_dependencies
from perfectframe.extractor_manager import ExtractorManager
from perfectframe.schemas import ExtractorName, ExtractorStatus, Message

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
    dependencies: Annotated[Dependencies, Depends(get_dependencies)],
) -> Message:
    """Run the provided extractor."""
    return ExtractorManager.start_extractor(extractor_name, background_tasks, dependencies)
