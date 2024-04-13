"""This module is designed to check and display CUDA availability
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
"""
import torch


def display_cuda_info() -> None:
    """Displays information about CUDA availability,
    CUDA version, and the number of CUDA devices.

    It's useful for quickly verifying the CUDA setup
    in a PyTorch-based deep learning environment.

    Outputs:
        - CUDA availability status (boolean).
        - Installed CUDA version.
        - Number of CUDA devices detected.
    """
    print(f"CUDA Available: {torch.cuda.is_available()}")
    print(f"CUDA Version: {torch.version.cuda}")
    print(f"CUDA Device Count: {torch.cuda.device_count()}")


if __name__ == "__main__":
    display_cuda_info()
