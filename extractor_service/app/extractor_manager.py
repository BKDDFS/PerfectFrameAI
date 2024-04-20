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
import logging
from typing import Type

from fastapi import HTTPException, BackgroundTasks

from .extractors import Extractor, ExtractorFactory
from .schemas import ExtractorConfig

logger = logging.getLogger(__name__)


class ExtractorManager:
    """Manages the execution of frame evaluation tasks within the application.

    This class orchestrates the evaluation process, ensuring that only one evaluator task is
    active at any given time. It manages the lifecycle of these tasks, from initiation to
    completion, and prevents concurrent executions to maintain system stability.

    Attributes:
        __active_evaluator (str | None): The name of the currently active evaluator class,
                                       or None if no evaluation process is underway.
    """
    __active_evaluator = None

    @classmethod
    def get_active_evaluator(cls):
        return cls.__active_evaluator

    @classmethod
    def start_extractor(cls, background_tasks: BackgroundTasks,
                        extractor_name: str,
                        config: ExtractorConfig) -> str:
        cls.check_is_already_extracting()
        extractor_class = ExtractorFactory.get_extractor(extractor_name)
        background_tasks.add_task(cls.__run_extractor, extractor_class, config)
        message = f"'{extractor_name}' started."
        return message

    @classmethod
    def __run_extractor(cls, extractor: Type[Extractor],
                        render_config: ExtractorConfig) -> None:
        try:
            cls.__active_evaluator = extractor.__name__
            extractor.process(render_config)
        finally:
            cls.__active_evaluator = None

    @classmethod
    def check_is_already_extracting(cls) -> None:
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
