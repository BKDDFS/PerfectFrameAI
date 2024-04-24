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
    """
    def __init__(self, config: ExtractorConfig) -> None:
        self.__active_extractor = None
        self.config = config

    @property
    def active_extractor(self):
        return self.__active_extractor

    def start_extractor(self, background_tasks: BackgroundTasks,
                        extractor_name: str) -> str:
        self.check_is_already_extracting()
        extractor_class = ExtractorFactory.get_extractor(extractor_name)
        background_tasks.add_task(self.__run_extractor, extractor_class)
        message = f"'{extractor_name}' started."
        return message

    def __run_extractor(self, extractor: Type[Extractor]) -> None:
        try:
            self.__active_extractor = extractor.__name__
            extractor(self.config).process()
        finally:
            self.__active_extractor = None

    def check_is_already_extracting(self) -> None:
        """Checks if an evaluation process is already active and raises an HTTPException if so.

        This method ensures that the system enforces the rule of having only one active
        evaluation process at any time.

        Raises:
            HTTPException: If an evaluation process is already active,
            to prevent concurrent evaluations.
        """
        if self.__active_extractor:
            error_massage = (
                f"Extractor '{self.__active_extractor}' is already running. "
                f"You can run only one extractor at the same time. "
                f"Wait until the evaluator is done before run next process."
            )
            logger.error(error_massage)
            raise HTTPException(status_code=409, detail=error_massage)
