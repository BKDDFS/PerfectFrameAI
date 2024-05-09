from pathlib import Path

import numpy as np


def test_list_directory_files(config, extractor):
    files = extractor._list_input_directory_files(config.images_extensions)
    assert isinstance(files, list)
    for file in files:
        assert isinstance(file, Path)


def test_read_images(config, extractor):
    files = extractor._list_input_directory_files(config.images_extensions)
    images = extractor._read_images(files)
    assert isinstance(images, list)
    for image in images:
        assert isinstance(image, np.ndarray)


def test_save_images(extractor, config, setup_best_frames_extractor_env):
    _ = setup_best_frames_extractor_env  # output_dir is best_frames not top_images
    files = list(config.output_directory.iterdir())
    assert not files

    files = extractor._list_input_directory_files(config.images_extensions)
    images = extractor._read_images(files)
    extractor._save_images(images)

    files = list(config.output_directory.iterdir())
    assert files
