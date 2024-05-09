import numpy as np


def test_extract_best_frames(extractor, files_dir, config):
    entries = list(files_dir.iterdir())
    assert len(entries) > 0, "None entries in files_dir found"
    videos = [
        entry for entry in entries
        if entry.is_file() and entry.suffix in config.video_extensions
    ]
    assert len(list(videos)) > 0, "None videos in files_dir found"

    extractor._get_image_evaluator()
    result = extractor._extract_best_frames(videos[0])

    assert isinstance(result, list)
    for frame in result:
        assert isinstance(frame, np.ndarray)
