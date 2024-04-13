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

import uvicorn
from fastapi import FastAPI

from app.pydantic_models import RequestData, Message, EvaluatorStatus
from app.top_frames_selector import TopFramesSelector
from app.best_frames_extractor import BestFramesExtractor
from app.evaluators_manager import EvaluatorsManager

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI()
evaluation_manager = EvaluatorsManager()


@app.get("/frames_evaluators/status")
def get_evaluators_status() -> EvaluatorStatus:
    """Provides the status of the currently active evaluator.

    Returns:
        EvaluatorStatus: A Pydantic model containing the name of the active evaluator.
    """
    return EvaluatorStatus(active_evaluator=evaluation_manager.active_evaluator)


@app.post("/frames_evaluators/best_frames_extractor")
def extract_best_frames(request_data: RequestData) -> Message:
    """Initiates the best frames extraction process based on the provided request data.

    Args:
        request_data (RequestData): A Pydantic model containing input and output folder paths.

    Returns:
        Message: A Pydantic model containing a message about the initiation status.
    """
    message = evaluation_manager.start_evaluation_process(BestFramesExtractor, request_data)
    return Message(message=message)


@app.post("/frames_evaluators/top_frames_selector")
def select_top_frames(request_data: RequestData) -> Message:
    """Initiates the top frames selection process based on the provided request data.

    Args:
        request_data (RequestData): A Pydantic model containing input and output folder paths.

    Returns:
        Message: A Pydantic model containing a message about the initiation status.
    """
    message = evaluation_manager.start_evaluation_process(TopFramesSelector, request_data)
    return Message(message=message)


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8100, reload=True)
