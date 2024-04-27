"""
This module provides manager class for running extractors and
managing extraction process lifecycle.
"""
import logging
from typing import Type

from fastapi import HTTPException, BackgroundTasks

from .extractors import Extractor, ExtractorFactory
from .schemas import ExtractorConfig

logger = logging.getLogger(__name__)


class ExtractorManager:
    """
    This class orchestrates extractors, ensuring that only one extractor is active at once,
    maintaining system stability.
    """
    __active_extractor = None

    @classmethod
    def get_active_extractor(cls) -> str:
        """
        Getter for class active extractor.

        Returns:
            str: Active extractor name.
        """
        return cls.__active_extractor

    def __init__(self, config: ExtractorConfig) -> None:
        """
        Initializes the manager with the given extractor configuration.

        Args:
            config (ExtractorConfig): A Pydantic model with configuration
                parameters for the extractor.
        """
        self.config = config

    def start_extractor(self, background_tasks: BackgroundTasks,
                        extractor_name: str) -> str:
        """
        Initializes the extractor class and runs the extraction process in the background.

        Args:
            background_tasks: A FastAPI tool for running tasks in background,
                which allows non-blocking operation of long-running tasks.
            extractor_name (str): The name of the extractor that will be used.

        Returns:
            str: Endpoint feedback message with started extractor name.
        """
        self._check_is_already_extracting()
        extractor_class = ExtractorFactory.get_extractor(extractor_name)
        background_tasks.add_task(self.__run_extractor, extractor_class)
        message = f"'{extractor_name}' started."
        return message

    def __run_extractor(self, extractor: Type[Extractor]) -> None:
        """
        Run extraction process and clean after it's done.

        Args:
            extractor (Extractor): Extractor that will be used for extraction.
        """
        try:
            self.__active_extractor = extractor.__name__
            extractor(self.config).process()
        finally:
            self.__active_extractor = None

    def _check_is_already_extracting(self) -> None:
        """
        Checks if some extractor is already active and raises an HTTPException if so.

        Raises:
            HTTPException: If extractor is already active to prevent concurrent extractions.
        """
        if self.__active_extractor:
            error_message = (
                f"Extractor '{self.__active_extractor}' is already running. "
                f"You can run only one extractor at the same time. "
                f"Wait until the extractor is done before run next process."
            )
            logger.error(error_message)
            raise HTTPException(status_code=409, detail=error_message)
