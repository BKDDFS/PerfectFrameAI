"""Provide manager class for running extractors and managing extraction process lifecycle.

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

from fastapi import BackgroundTasks, HTTPException

from perfectframe.dependencies import ExtractorDependencies
from perfectframe.extractors import Extractor, ExtractorFactory
from perfectframe.schemas import ExtractorConfig, ExtractorName

logger = logging.getLogger(__name__)


class ExtractorManager:
    """Orchestrate extractors, ensuring that only one extractor is active at once."""

    _active_extractor = None

    @classmethod
    def get_active_extractor(cls) -> str | None:
        """Return the active extractor name."""
        return cls._active_extractor

    @classmethod
    def start_extractor(
        cls,
        extractor_name: ExtractorName,
        background_tasks: BackgroundTasks,
        config: ExtractorConfig,
        dependencies: ExtractorDependencies,
    ) -> str:
        """Initialize the extractor class and run the extraction process in the background."""
        cls._check_is_already_extracting()
        extractor = ExtractorFactory.create_extractor(extractor_name, config, dependencies)
        background_tasks.add_task(cls.__run_extractor, extractor, extractor_name)
        return f"'{extractor_name}' started."

    @classmethod
    def __run_extractor(cls, extractor: Extractor, extractor_name: ExtractorName) -> None:
        """Run extraction process and clean after it's done."""
        try:
            cls._active_extractor = extractor_name
            extractor.process()
        finally:
            cls._active_extractor = None

    @classmethod
    def _check_is_already_extracting(cls) -> None:
        """Check if some extractor is already active and raise an HTTPException if so."""
        if cls._active_extractor:
            error_message = (
                f"Extractor '{cls._active_extractor}' is already running. "
                f"You can run only one extractor at the same time. "
                f"Wait until the extractor is done before run next process."
            )
            logger.error(error_message)
            raise HTTPException(status_code=409, detail=error_message)
