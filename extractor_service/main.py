"""This module defines a FastAPI web application for managing frame evaluation processes.

The application provides functionality to start and monitor frame evaluation tasks such
as extracting the best frames and selecting the top frames from given input.
It is designed to run one evaluation process at a time and offers API
endpoints to initiate these processes and check their current status.
Evaluation processes are executed in the background using
threading, and their states are managed through the `EvaluatorsManager` class.

Endpoints:
    GET /frames_evaluators/status:
        Provides the status of the active evaluator.
    POST /frames_evaluators/best_frames_extractor:
        Initiates the best frames extraction process.
    POST /frames_evaluators/top_frames_selector:
        Initiates the top frames selection process.
"""
import logging
import sys

import uvicorn
from fastapi import FastAPI, BackgroundTasks, Depends

from app.schemas import ExtractorConfig, Message, EvaluatorStatus
from app.extractor_manager import ExtractorManager

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    handlers=[logging.StreamHandler(sys.stdout)])
logger = logging.getLogger(__name__)

app = FastAPI()


@app.post("/image_extractors/{extractor_name}")
def extract_best_frames(background_tasks: BackgroundTasks, extractor_name: str,
                        config: ExtractorConfig = Depends()) -> Message:
    """Initiates the best frames extraction process based on the provided request data.

    Args:
        request_data (RequestData): A Pydantic model containing input and output folder paths.

    Returns:
        Message: A Pydantic model containing a message about the initiation status.
        :param extractor_name:
        :param background_tasks:
        :param config:
    """
    message = ExtractorManager.start_extractor(background_tasks, extractor_name, config)
    return Message(message=message)


@app.get("/status")
def get_evaluators_status() -> EvaluatorStatus:
    """Provides the status of the currently active evaluator.

    Returns:
        EvaluatorStatus: A Pydantic model containing the name of the active evaluator.
    """
    return EvaluatorStatus(active_evaluator=ExtractorManager.get_active_evaluator())


@app.get("/health")
async def health_check():
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=8100, reload=True)
