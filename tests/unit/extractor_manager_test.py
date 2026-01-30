import http

import pytest
from fastapi import BackgroundTasks, HTTPException

from perfectframe.extractor_manager import ExtractorManager
from perfectframe.extractors import ExtractorFactory
from perfectframe.schemas import ExtractorName, Message


def test_get_active_extractor():
    assert ExtractorManager.get_active_extractor() is None


def test_start_extractor(mocker, dependencies):
    mock_checking = mocker.patch.object(ExtractorManager, "_check_is_already_extracting")
    mock_create_extractor = mocker.patch.object(ExtractorFactory, "create_extractor")
    extractor_name = ExtractorName.BEST_FRAMES
    mock_extractor = mocker.MagicMock()
    mock_background_tasks = mocker.MagicMock(spec=BackgroundTasks)
    mock_create_extractor.return_value = mock_extractor

    message = ExtractorManager.start_extractor(extractor_name, mock_background_tasks, dependencies)

    mock_checking.assert_called_once()
    assert ExtractorManager._active_extractor == extractor_name
    mock_create_extractor.assert_called_once_with(extractor_name, dependencies)
    mock_background_tasks.add_task.assert_called_once_with(
        ExtractorManager._ExtractorManager__run_extractor,
        mock_extractor,
    )
    expected_message = Message(message=f"'{extractor_name.value}' started.")
    assert message == expected_message, "The return message does not match expected."
    ExtractorManager._active_extractor = None


def test_run_extractor(mocker):
    mock_extractor = mocker.patch("perfectframe.extractors.BestFramesExtractor")

    ExtractorManager._ExtractorManager__run_extractor(mock_extractor)

    mock_extractor.process.assert_called_once()


def test_run_extractor_logs_exception_on_failure(mocker, caplog):
    mock_extractor = mocker.MagicMock()
    mock_extractor.process.side_effect = RuntimeError("Test error")

    with caplog.at_level("ERROR"):
        ExtractorManager._ExtractorManager__run_extractor(mock_extractor)

    mock_extractor.process.assert_called_once()
    assert "Extraction failed with error" in caplog.text
    assert ExtractorManager._active_extractor is None


def test_check_is_already_evaluating_true():
    test_extractor = ExtractorName.BEST_FRAMES
    ExtractorManager._active_extractor = test_extractor
    expected_error_message = (
        f"Extractor '{test_extractor.value}' is already running. "
        f"You can run only one extractor at the same time. "
        f"Wait until the extractor is done before run next process."
    )

    with pytest.raises(HTTPException, match=expected_error_message) as exc_info:
        ExtractorManager._check_is_already_extracting()

    assert exc_info.value.status_code == http.HTTPStatus.CONFLICT
    ExtractorManager._active_extractor = None
