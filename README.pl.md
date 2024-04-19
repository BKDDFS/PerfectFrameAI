# Images Extractors AI
English version: [EN](README.md)
#### Video Demo: <>

### Wymagania:
- Niezależnie od wybranego sposobu instalacji musisz mieć zainstalowanego dockera dla ułatwienia instalacji np. docker desktop:
<https://www.docker.com/products/docker-desktop/>
- Musisz mieć zainstalowanego pythona.
- Przetwarzanie obrazów/filmów to wymagające obliczeniowo zadania. Zalecam korzystanie z projektu tylko na PC z GPU ze rdzeniami CUDA (Nvidia).
- Musisz przygotować video (.mp4) i/lub obrazy (.jpg) jako input. Możesz je umieścić w domyślnym folderze 'input_directory' dla ułatwienia, ale nie musisz.

### Instalacja:
Upewnij się, że spełniasz wymagania opisane wyżej.
#### Sposób 1:
Najszybszy sposób to włączenie jednego ze skryptów demonstracyjnych:
- **quick_demo.bat(Windows)**
- **quick_demo.ssh(Linux/Mac)** \
Skypty korzystają z wartości domyślnych: \
**extractor:** best_frames_extractor \
**input_directory:** ./input_directory \
**output_directory:** ./output_directory \
**port:** 8100

#### Sposób 2:
Sposób drugi w dalszym ciągu korzysta z automatycznego setupu. Natomiast włączając go za pomocą cmd setup.py daje możliwość zmiany domyślnych parametrów. \
Możesz włączać różne extractory. \
**Przykład:** \
`python setup.py best_frames_extractor` \
albo \
`python setup.py top_images_extractor` \
Możemy skonfigurować także inne parametry używając flag: \
**--port, -p** -> do zmiany portu na którym będzie działał extractor service (domyślnie 8100) \
**--input, -i** -> do zmiany lokalizacji, w której jest input (video/obrazy do ekstrakcji z nich najelpszych obrazów) (domyślnie jest input_directory) \
**--output, -o** -> do zmiany lokalizacji, w której będzie output (najlepsze obrazy) (domyślnie jest output_directory) \
**Przykład:** \
`python setup.py best_frames_extractor -p <your_port_here> -i <your_input_dir_here> -o <your_output_dir_here>` \
Note: Inne domyślne parametry możesz edytować w config.py. (Upewnij się że wiesz co robisz..)

### Sposób 3:
Ten sposób polega na zrobieniu ręcznie tego co robi setup.py.
**Krok 1:** \
Stworzenie obrazu z Dockerfile. \
`docker build -t extractor_service_image ./extractor_service` \
**Krok 2:** \
Utworzenie kontenera z obrazu z wybranymi ścieżkami i portem, dając mu dostęp do GPU. Zmień domyślne wartości wedle uznania, ale pamiętaj, że  \
`docker run --name extractor_service --gpus all -p 8100:8100 -v ./input_directory:/app/input_directory -v ./output_directory:/app/output_directory -d extractor_service_image` \
Note: 
**Krok 3:** \
Wysłanie `` \
**Krok 1:** Skorzystaj ze skryptu z wybranym extractorem.\

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