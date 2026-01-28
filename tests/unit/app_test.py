from fastapi import BackgroundTasks

from perfectframe.app import get_extractors_status, health_check, run_extractor
from perfectframe.extractor_manager import ExtractorManager
from perfectframe.schemas import ExtractorName, Message


def test_health_check():
    result = health_check()

    assert result == {"status": "healthy"}


def test_get_extractors_status(mocker):
    mocker.patch.object(
        ExtractorManager, "get_active_extractor", return_value=ExtractorName.BEST_FRAMES
    )

    result = get_extractors_status()

    assert result.active_extractor == ExtractorName.BEST_FRAMES


def test_run_extractor(mocker, config, dependencies):
    expected_message = Message(message="'best_frames_extractor' started.")
    mock_start = mocker.patch.object(
        ExtractorManager, "start_extractor", return_value=expected_message
    )
    mock_background_tasks = mocker.MagicMock(spec=BackgroundTasks)

    result = run_extractor(
        extractor_name=ExtractorName.BEST_FRAMES,
        background_tasks=mock_background_tasks,
        dependencies=dependencies,
        config=config,
    )

    mock_start.assert_called_once_with(
        ExtractorName.BEST_FRAMES, mock_background_tasks, config, dependencies
    )
    assert result == expected_message
