"""
This module provides manager class for running extractors and
managing extraction process lifecycle.
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

from fastapi import HTTPException, BackgroundTasks

from .dependencies import ExtractorDependencies
from .extractors import Extractor, ExtractorFactory
from .schemas import ExtractorConfig

logger = logging.getLogger(__name__)


class ExtractorManager:
    """
    This class orchestrates extractors, ensuring that only one extractor is active at once,
    maintaining system stability.
    """
    _active_extractor = None

    @classmethod
    def get_active_extractor(cls) -> str:
        """
        Getter for class active extractor.

        Returns:
            str: Active extractor name.
        """
        return cls._active_extractor

    @classmethod
    def start_extractor(cls, extractor_name: str, background_tasks: BackgroundTasks,
                        config: ExtractorConfig, dependencies: ExtractorDependencies) -> str:
        """
        Initializes the extractor class and runs the extraction process in the background.

        Args:
            extractor_name (str): The name of the extractor that will be used.
            background_tasks (BackgroundTasks): A FastAPI tool for running tasks in background.
            config (ExtractorConfig): A Pydantic model with extractor configuration.
            dependencies(ExtractorDependencies): Dependencies that will be used in extractor.

        Returns:
            str: Endpoint feedback message with started extractor name.
        """
        cls._check_is_already_extracting()
        extractor = ExtractorFactory.create_extractor(extractor_name, config, dependencies)
        background_tasks.add_task(cls.__run_extractor, extractor, extractor_name)
        message = f"'{extractor_name}' started."
        return message

    @classmethod
    def __run_extractor(cls, extractor: Extractor, extractor_name: str) -> None:
        """
        Run extraction process and clean after it's done.

        Args:
            extractor (Extractor): Extractor that will be used for extraction.
            extractor_name (str): The name of the extractor that will be used.
        """
        try:
            cls._active_extractor = extractor_name
            extractor.process()
        finally:
            cls._active_extractor = None

    @classmethod
    def _check_is_already_extracting(cls) -> None:
        """
        Checks if some extractor is already active and raises an HTTPException if so.

        Raises:
            HTTPException: If extractor is already active to prevent concurrent extractions.
        """
        if cls._active_extractor:
            error_message = (
                f"Extractor '{cls._active_extractor}' is already running. "
                f"You can run only one extractor at the same time. "
                f"Wait until the extractor is done before run next process."
            )
            logger.error(error_message)
            raise HTTPException(status_code=409, detail=error_message)
