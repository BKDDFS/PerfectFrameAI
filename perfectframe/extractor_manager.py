"""Provide manager class for running extractors and managing extraction process lifecycle."""

import logging
import threading

from fastapi import BackgroundTasks, HTTPException

from perfectframe.dependencies import Dependencies
from perfectframe.extractors import Extractor, ExtractorFactory
from perfectframe.schemas import ExtractorName, Message

logger = logging.getLogger(__name__)


class ExtractorManager:
    """Orchestrate extractors, ensuring that only one extractor is active at once."""

    _active_extractor: ExtractorName | None = None
    _lock = threading.Lock()

    @classmethod
    def get_active_extractor(cls) -> ExtractorName | None:
        """Return the active extractor name."""
        with cls._lock:
            return cls._active_extractor

    @classmethod
    def start_extractor(
        cls,
        extractor_name: ExtractorName,
        background_tasks: BackgroundTasks,
        dependencies: Dependencies,
    ) -> Message:
        """Initialize the extractor class and run the extraction process in the background."""
        with cls._lock:
            cls._check_is_already_extracting()
            cls._active_extractor = extractor_name
        extractor = ExtractorFactory.create_extractor(extractor_name, dependencies)
        background_tasks.add_task(cls.__run_extractor, extractor)
        return Message(message=f"'{extractor_name.value}' started.")

    @classmethod
    def __run_extractor(cls, extractor: Extractor) -> None:
        """Run extraction process and clean after it's done."""
        try:
            extractor.process()
        finally:
            with cls._lock:
                cls._active_extractor = None

    @classmethod
    def _check_is_already_extracting(cls) -> None:
        """Check if some extractor is already active and raise an HTTPException if so."""
        if cls._active_extractor:
            error_message = (
                f"Extractor '{cls._active_extractor.value}' is already running. "
                f"You can run only one extractor at the same time. "
                f"Wait until the extractor is done before run next process."
            )
            logger.error(error_message)
            raise HTTPException(status_code=409, detail=error_message)
