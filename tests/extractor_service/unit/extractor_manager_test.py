from unittest.mock import patch, MagicMock

import pytest
from fastapi import HTTPException, BackgroundTasks

from extractor_service.app.extractor_manager import ExtractorManager
from extractor_service.app.extractors import ExtractorFactory


def test_get_active_extractor():
    assert ExtractorManager.get_active_extractor() is None


@patch.object(ExtractorFactory, "create_extractor")
@patch.object(ExtractorManager, "_check_is_already_extracting")
def test_start_extractor(mock_checking, mock_create_extractor, config):
    extractor_name = "some_extractor"
    mock_extractor_class = MagicMock()
    mock_background_tasks = MagicMock(spec=BackgroundTasks)
    mock_create_extractor.return_value = mock_extractor_class

    message = ExtractorManager.start_extractor(mock_background_tasks, config, extractor_name)

    mock_checking.assert_called_once()
    mock_create_extractor.assert_called_once_with(extractor_name)
    mock_background_tasks.add_task.assert_called_once_with(
        ExtractorManager._ExtractorManager__run_extractor,
        mock_extractor_class,
        extractor_name
    )
    expected_message = f"'{extractor_name}' started."
    assert message == expected_message, "The return message does not match expected."


@patch("extractor_service.app.extractors.BestFramesExtractor")
def test_run_extractor(mock_extractor):
    extractor_name = "some_extractor"
    mock_extractor.return_value.process = MagicMock()
    mock_extractor.__name__ = MagicMock()

    ExtractorManager._ExtractorManager__run_extractor(mock_extractor, extractor_name)

    mock_extractor.assert_called_once()


def test_check_is_already_evaluating_true():
    test_extractor = "active_extractor"
    ExtractorManager._active_extractor = test_extractor
    expected_error_massage = (
        f"Extractor '{test_extractor}' is already running. "
        f"You can run only one extractor at the same time. "
        f"Wait until the extractor is done before run next process."
    )

    with pytest.raises(HTTPException, match=expected_error_massage) as exc_info:
        ExtractorManager._check_is_already_extracting()

    assert exc_info.value.status_code == 409
