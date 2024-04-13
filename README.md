# Frames Evaluators Project

#### Video Demo: <https://www.youtube.com/watch?v=5qIiYmVvFzE>

#### Description:

The tool is designed for evaluating and selecting best looking frames from video content, utilizing advanced image processing techniques.

### Features:

- ### Frames Evaluator Status:
    #### GET /:
    Initially, check the status of the frames' evaluator. If no evaluator is active, proceed to the next step.

- ### Run Best Frames Evaluator: 
    #### POST /frames_evaluators/best_frames_extractor
    Input the folder with videos to start extracting the best frames. The progress can be monitored as frames start appearing in the output folder.

- ### Run Top Frames Selector:
    #### POST /frames_evaluators/top_frames_selector
    Once the best frames are extracted, activate this feature. It will process the extracted frames and select the best among them based on the defined criteria.

## Installation:
This project requires specific dependencies to be installed and set up properly.
Follow these steps to ensure everything is ready for use:

### Step 1: Install Required Libraries
First, install the necessary libraries listed in requirements.txt.
You can do this by running the following command in your terminal:

`pip install -r requirements.txt`

### Step 2: Install CUDA 1.2.1
Ensure that you have CUDA version 1.2.1 installed on your system.
CUDA is necessary for running operations on the GPU.
You can download and install it from the NVIDIA CUDA Toolkit website.

### Step 3: Install PyTorch with CUDA Support
Install PyTorch, torchvision, and torchaudio with CUDA 1.2.1 support using the following pip command:

`pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121`

### Step 4: Verify CUDA Availability
To check if CUDA is properly installed and available for PyTorch,
use the display_cuda_info.py script.
Run the script, and you should see an output indicating that CUDA is available:

`python display_cuda_info.py`

You must see the output:
#### CUDA Available: True

If you see CUDA Available: True, then you're all set! If not, you may need to troubleshoot your CUDA installation.


## Modules description:

**project.py**

This module defines a Flask web application for managing frame evaluation processes.

The application allows users to start and monitor different frame evaluation processes
such as extracting best frames and selecting top frames from a given input. It supports
running one evaluation process at a time and provides endpoints to start these processes
and check their status. The application uses threading to run evaluation processes in
the background and manages their state through the AppManager class.

Classes:
    AppManager: Manages the state and configuration of the application.

Endpoints:
    GET /: Provides the status of the active evaluator.
    POST /frames_evaluators/best_frames_extractor: Initiates the best frames extraction process.
    POST /frames_evaluators/top_frames_selector: Initiates the top frames selection process.

**evaluator.py:**

This module provides the Evaluator abstract class, designed for video and image
evaluation tasks using various image quality assessment (IQA) metrics.

The module integrates functionalities from libraries such as OpenCV, PyTorch, Numpy,
and PyIQA, offering tools to process and evaluate image and video data. It supports
operations like converting image formats, applying transformations, scoring frames, and
saving results.

Classes:
    Evaluator: An abstract base class for creating specific evaluators for image and
               video analysis tasks, leveraging different IQA metrics and processing
               techniques.

**best_frames_extractor.py:**

This module provides the BestFramesExtractor class, an implementation of the Evaluator
abstract class, used for extracting the best frames from video files in a given folder.

The module leverages OpenCV for video processing and numpy for numerical operations. It
includes functionalities to process multiple video files, filter them based on format and
processing status, and extract and save the best frames from each video.

Classes:
    BestFramesExtractor: Extracts best frames from video files.

How to Use:
    To use the BestFramesExtractor, instantiate it and call the `process` method with the
    path to the folder containing video files.

**top_frames_selector.py:**

This module provides the TopFramesSelector class
for selecting the top frames from a series of images.
It is designed for image and video evaluation tasks that
require identifying and processing the most significant frames based on
specific image quality assessment (IQA) metrics.

Classes:
    TopFramesSelector: Extends the Evaluator class to select and
    process the top frames from a set of images. It includes methods
    for loading frames from a specified folder, scoring each frame using
    IQA metrics, and saving the top-scored frames based on a percentile threshold.

Usage:
    This class is intended to be used in scenarios where it's crucial to
    identify and process the most significant or highest quality frames from a
    collection of images, such as in video analysis, quality control in image processing,
    or content curation in media applications.

**display_cuda_info.py**

This module is designed to check and display CUDA availability
and related information in a PyTorch environment.
It provides a quick and efficient way to determine
if CUDA is available on the current system,
the version of CUDA installed,
and the number of CUDA devices (GPUs) detected by PyTorch.

Functions:
    - display_cuda_info(): Checks and displays
    information about CUDA availability, version, and device count.

Usage:
    This module is intended to be run
    as a script to quickly check CUDA related configurations.
    It's especially useful during the setup of deep learning
    environments or when troubleshooting issues related to PyTorch
    and CUDA compatibility.