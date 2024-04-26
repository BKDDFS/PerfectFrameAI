from unittest.mock import patch, call

import torch
import pytest

from extractor_service.app.check_cuda import check_cuda_availability


@pytest.mark.parametrize("is_available", (True, False))
@patch("torch.cuda.is_available")
@patch("torch.cuda.device_count")
@patch("builtins.print")
def test_check_cuda_availability(mock_print, mock_device_count, mock_is_available, is_available):
    version = "10.2"
    device_count = 2
    torch.version.cuda = version
    mock_is_available.return_value = is_available
    mock_device_count.return_value = device_count

    assert check_cuda_availability(True) == is_available, "Should return True for CUDA availability"
    if is_available:
        expected_calls = [
            call(f"CUDA Available: {True}"),
            call(f"CUDA Version: {version}"),
            call(f"CUDA Device Count: {device_count}")
        ]
        mock_print.assert_has_calls(expected_calls, any_order=True)
    else:
        mock_print.assert_not_called()

    mock_print.reset_mock()
    assert check_cuda_availability(False) == is_available, "Should return True for CUDA availability"
    mock_print.assert_not_called()
