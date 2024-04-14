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
from fastapi import HTTPException, BackgroundTasks

from .evaluator import Evaluator
from .schemas import RequestData, EvaluatorConfig

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
    __active_evaluator = None

    @classmethod
    def start_evaluator(cls, background_tasks: BackgroundTasks,
                        evaluator_name: str,
                        evaluator_config: EvaluatorConfig) -> str:
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
        cls.check_is_already_evaluating()
        evaluator_class = EvaluatorFactory.get_evaluator(evaluator_name)
        background_tasks.add_task(cls.__run_evaluator, evaluator_class, evaluator_config)
        cls.__active_evaluator = evaluator_class.__name__
        message = f"'{cls.__active_evaluator}' started."
        return message

    @classmethod
    def __run_evaluator(cls, evaluator: Evaluator,
                        render_config: EvaluatorConfig) -> None:
        try:
            evaluator.process()
        finally:
            cls.__active_evaluator = None

    @classmethod
    def check_is_already_evaluating(cls) -> None:
        """Checks if an evaluation process is already active and raises an HTTPException if so.

        This method ensures that the system enforces the rule of having only one active
        evaluation process at any time.

        Raises:
            HTTPException: If an evaluation process is already active,
            to prevent concurrent evaluations.
        """
        error_massage = (f"Evaluator '{cls.__active_evaluator}' is already running. "
                         f"You can run only one evaluator at the same time. "
                         f"Wait until the evaluator is done before run next process.")
        if cls.__active_evaluator:
            logger.error(error_massage)
            raise HTTPException(status_code=409, detail=error_massage)
