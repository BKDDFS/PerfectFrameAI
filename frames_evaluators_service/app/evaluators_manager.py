"""This module provides the core functionality for managing frame
evaluation processes within a FastAPI application.

It defines the `EvaluatorsManager` class,
which orchestrates the initiation and management of frame evaluation tasks.

Key Components:
- `EvaluatorsManager`:
    A class that manages the lifecycle of frame evaluation processes.
    It controls the initiation of new processes,
    monitors their execution in background threads,
    and maintains the status of the currently active evaluator.
"""
import threading
import logging
from fastapi import HTTPException

from app.evaluator import Evaluator
from app.pydantic_models import RequestData

logger = logging.getLogger(__name__)


class EvaluatorsManager:
    """Manages the execution of frame evaluation tasks within the application.

    This class orchestrates the evaluation process, ensuring that only one evaluator task is
    active at any given time. It manages the lifecycle of these tasks, from initiation to
    completion, and prevents concurrent executions to maintain system stability.

    Attributes:
        active_evaluator (str | None): The name of the currently active evaluator class,
                                       or None if no evaluation process is underway.
    """
    def __init__(self):
        self.active_evaluator = None

    def start_evaluation_process(self, evaluator_class: Evaluator,
                                 request_data: RequestData) -> str:
        """Starts a new evaluation process, ensuring no other process is currently active.

        This function initiates a background thread for the evaluation process, updating
        the active evaluator status accordingly.

        Args:
            evaluator_class (type[Evaluator]):
                The evaluator class to be instantiated and used for the evaluation.
            request_data (RequestData):
                The data required for the evaluation process,
                including input and output directories.

        Returns:
            str: A message indicating the start of the evaluation process.

        Raises:
            HTTPException: If an evaluation process is already active.
        """
        self.check_is_already_evaluating()
        thread = threading.Thread(target=self.__background_process,
                                  args=(evaluator_class, request_data))
        thread.start()
        self.active_evaluator = evaluator_class.__name__
        message = f"'{self.active_evaluator}' started."
        return message

    def __background_process(self, evaluator_class: Evaluator,
                             request_data: RequestData) -> None:
        """Executes the evaluation process in a background thread.

        Instantiates the evaluator and processes the frames as specified in `request_data`.
        This method is designed to run in the background and will clear the active evaluator
        upon completion or failure.

        Args:
            evaluator_class (type[Evaluator]): The evaluator class to instantiate.
            request_data (RequestData): Contains the paths for input and
            output data necessary for the process.
        """
        try:
            evaluator = evaluator_class(request_data.output_folder)
            evaluator.process(request_data.input_folder)
        finally:
            self.active_evaluator = None

    def check_is_already_evaluating(self) -> None:
        """Checks if an evaluation process is already active and raises an HTTPException if so.

        This method ensures that the system enforces the rule of having only one active
        evaluation process at any time.

        Raises:
            HTTPException: If an evaluation process is already active,
            to prevent concurrent evaluations.
        """
        error = (f"Evaluator '{self.active_evaluator}' is already running. "
                 f"You can run only one evaluator at the same time. "
                 f"Wait until the evaluator is done before run next process")
        if self.active_evaluator:
            logger.error(error)
            raise HTTPException(status_code=409, detail=error)
