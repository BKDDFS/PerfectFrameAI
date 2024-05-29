def test_extract_best_frames(extractor, config, setup_best_frames_extractor_env):
    input_dir, output_dir, _ = setup_best_frames_extractor_env
    entries = list(input_dir.iterdir())
    assert len(entries) > 0, "None entries in files_dir found"
    videos = [
        entry for entry in entries
        if entry.is_file() and entry.suffix in config.video_extensions
    ]
    assert len(list(videos)) > 0, "None videos in files_dir found"
    assert not any(output_dir.iterdir()), "Output dir has entries before test"

    extractor._get_image_evaluator()
    extractor._extract_best_frames(videos[0])

    assert any(output_dir.iterdir()), "Output dir is empty."
