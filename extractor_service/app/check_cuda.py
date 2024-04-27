"""
This module is designed to check and display CUDA availability.
"""
import torch


def check_cuda_availability(print_info: bool = True) -> bool:
    """
    It checks is cuda available.
    If print info is True,
    this function displays information about CUDA availability,
    CUDA version, and the number of CUDA devices.

    Outputs:
        - CUDA availability status (boolean).
        - Installed CUDA version.
        - Number of CUDA devices detected.

    Returns:
        bool: CUDA cores availability.
    """
    cuda_availability = torch.cuda.is_available()
    if print_info and cuda_availability:
        print(f"CUDA Available: {cuda_availability}")
        print(f"CUDA Version: {torch.version.cuda}")
        print(f"CUDA Device Count: {torch.cuda.device_count()}")
    return cuda_availability


if __name__ == "__main__":
    check_cuda_availability()
