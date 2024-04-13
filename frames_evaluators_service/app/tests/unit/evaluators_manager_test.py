import pytest
from fastapi import HTTPException
from unittest.mock import patch, Mock
from app.evaluators_manager import EvaluatorsManager
from app.top_frames_selector import TopFramesSelector

EXAMPLE_EVALUATOR = TopFramesSelector
TEST_EVALUATOR = Mock()


@pytest.fixture
def manager():
    manager = EvaluatorsManager()
    yield manager


class RequestData:
    input_folder = "input/path"
    output_folder = "output/path"


def test_is_active_evaluator_default(manager):
    assert manager.active_evaluator is None


def test_start_evaluation_process(manager):
    manager.check_is_already_evaluating = Mock()
    mock_thread = Mock()
    with patch("app.evaluators_manager.threading.Thread", return_value=mock_thread) as mock_threading:
        massage = manager.start_evaluation_process(EXAMPLE_EVALUATOR, RequestData)
        assert manager.active_evaluator == "TopFramesSelector"
        assert massage == f"'{manager.active_evaluator}' started."
    manager.check_is_already_evaluating.assert_called_once()
    mock_threading.assert_called_once()
    mock_thread.start.assert_called_once()


def test_background_process(manager):
    mock_evaluator = Mock()
    mock_evaluator_class = Mock(return_value=mock_evaluator)
    manager._EvaluatorsManager__background_process(mock_evaluator_class, RequestData)
    mock_evaluator_class.assert_called_with(RequestData.output_folder)
    mock_evaluator.process.assert_called_with(RequestData.input_folder)
    assert manager.active_evaluator is None


def test_check_is_already_evaluating_true(manager):
    manager.active_evaluator = "active_evaluator"
    expected_error_detail = ("Evaluator 'active_evaluator' is already running. "
                             "You can run only one evaluator at the same time. "
                             "Wait until the evaluator is done before run next process")
    with pytest.raises(HTTPException) as exc_info:
        manager.check_is_already_evaluating()

    assert exc_info.value.status_code == 409
    assert exc_info.value.detail == expected_error_detail


def test_check_is_already_evaluating_false(manager):
    manager.check_is_already_evaluating()
