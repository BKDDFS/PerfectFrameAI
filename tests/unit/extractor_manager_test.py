import http

import pytest
from fastapi import BackgroundTasks, HTTPException
from pytest_mock import MockerFixture

from perfectframe.extractor_manager import ExtractorManager
from perfectframe.extractors import ExtractorFactory


def test_get_active_extractor():
    assert ExtractorManager.get_active_extractor() is None


def test_start_extractor(mocker: MockerFixture, config, dependencies):
    mock_checking = mocker.patch.object(ExtractorManager, "_check_is_already_extracting")
    mock_create_extractor = mocker.patch.object(ExtractorFactory, "create_extractor")
    extractor_name = "some_extractor"
    mock_extractor = mocker.MagicMock()
    mock_background_tasks = mocker.MagicMock(spec=BackgroundTasks)
    mock_create_extractor.return_value = mock_extractor

    message = ExtractorManager.start_extractor(
        extractor_name, mock_background_tasks, config, dependencies
    )

    mock_checking.assert_called_once()
    mock_create_extractor.assert_called_once_with(extractor_name, config, dependencies)
    mock_background_tasks.add_task.assert_called_once_with(
        ExtractorManager._ExtractorManager__run_extractor,
        mock_extractor,
        extractor_name,
    )
    expected_message = f"'{extractor_name}' started."
    assert message == expected_message, "The return message does not match expected."


def test_run_extractor(mocker: MockerFixture):
    mock_extractor = mocker.patch("perfectframe.extractors.BestFramesExtractor")
    extractor_name = "some_extractor"

    ExtractorManager._ExtractorManager__run_extractor(mock_extractor, extractor_name)

    mock_extractor.process.assert_called_once()


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

    assert exc_info.value.status_code == http.HTTPStatus.CONFLICT
