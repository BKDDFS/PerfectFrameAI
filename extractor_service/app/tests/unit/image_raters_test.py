@pytest.mark.parametrize("is_available", (True, False))
def test_get_torch_device(evaluator, is_available, caplog):
    with patch("torch.cuda.is_available", return_value=is_available) as mock_cuda_is_available:
        with caplog.at_level(logging.DEBUG):
            result = evaluator.get_torch_device()
        mock_cuda_is_available.assert_called_once()
    if is_available:
        assert "Using CUDA for processing." in caplog.messages[0]
        assert result.type == 'cuda'
    else:
        assert "CUDA is not available!!! Using CPU for processing." in caplog.messages[0]
        assert result.type == 'cpu'
    assert isinstance(result, torch.device)


def test_score_frame(evaluator, caplog):
    evaluator.convert_frame_bgr_to_rgb = Mock(return_value=TEST_RGB_FRAME)
    evaluator.convert_frame_rgb_to_tensor = Mock(return_value=TEST_TENSOR_FRAME)
    evaluator.iqa_metric = MagicMock(return_value=MagicMock())
    evaluator.iqa_metric.return_value.item = MagicMock(return_value=EXPECTED_RESULT)
    with caplog.at_level(logging.DEBUG):
        result = evaluator._score_frame(TEST_BGR_FRAME)
    evaluator.convert_frame_bgr_to_rgb.assert_called_once_with(TEST_BGR_FRAME)
    evaluator.convert_frame_rgb_to_tensor.assert_called_once_with(TEST_RGB_FRAME,
                                                                  evaluator.transforms_compose, evaluator.device)
    evaluator.iqa_metric.return_value.item.assert_called_once()
    assert f"Frame scored. Score: {result}" in caplog.messages[0]
    assert result == EXPECTED_RESULT

def test_convert_frame_rgb_to_tensor(evaluator, caplog):
    evaluator.transforms_compose = MagicMock(return_value=MagicMock())
    evaluator.transforms_compose.return_value.unsqueeze = MagicMock(return_value=MagicMock())
    evaluator.transforms_compose.return_value.unsqueeze.return_value.to = MagicMock(return_value=EXPECTED_RESULT)
    with caplog.at_level(logging.DEBUG):
        result = evaluator.convert_frame_rgb_to_tensor(TEST_RGB_FRAME, evaluator.transforms_compose, evaluator.device)
    evaluator.transforms_compose.assert_called_once_with(TEST_RGB_FRAME)
    evaluator.transforms_compose.return_value.unsqueeze.assert_called_once_with(0)
    evaluator.transforms_compose.return_value.unsqueeze.return_value.to.assert_called_once_with(evaluator.device)
    assert "Frame converted from RGB to TENSOR." in caplog.messages[0]
    assert result == EXPECTED_RESULT