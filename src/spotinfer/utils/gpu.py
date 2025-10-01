"""GPU utility functions for pattern matching and type extraction."""

import re
from typing import List, Optional

# Common GPU patterns for extracting GPU types from descriptions
GPU_PATTERNS = [
    r"(B300)\s+SXM6",  # e.g., "B300 SXM6"
    r"(B200)\s+SXM6",  # e.g., "B200 SXM6"
    r"(H200)\s+SXM5",  # e.g., "H200 SXM5"
    r"(H100)\s+SXM5",  # e.g., "H100 SXM5"
    r"(A100)\s+SXM4",  # e.g., "A100 SXM4"
    r"(RTX\s+PRO)\s+6000",  # e.g., "RTX PRO 6000"
    r"(RTX\s+6000)\s+Ada",  # e.g., "RTX 6000 Ada"
    r"(RTX\s+A6000)",  # e.g., "RTX A6000"
    r"(Tesla\s+V100)",  # e.g., "Tesla V100"
    r"(L40S)",  # e.g., "L40S"
]


def extract_gpu_type(gpu_description: str) -> Optional[str]:
    """
    Extract GPU type from a GPU description string.

    Args:
        gpu_description: The GPU description string to parse

    Returns:
        The extracted GPU type if found, None otherwise

    Examples:
        >>> extract_gpu_type("1x B300 SXM6 262GB")
        "B300"
        >>> extract_gpu_type("1x RTX PRO 6000 96GB")
        "RTX PRO"
        >>> extract_gpu_type("1x Tesla V100 16GB")
        "Tesla V100"
        >>> extract_gpu_type("No GPU")
        None
    """
    if not gpu_description:
        return None

    for pattern in GPU_PATTERNS:
        match = re.search(pattern, gpu_description)
        if match:
            return match.group(1)

    return None


def get_available_gpu_types_from_instances(instance_types: List) -> List[str]:
    """
    Extract unique GPU types from a list of instance types.

    Args:
        instance_types: List of instance type objects with gpu attribute

    Returns:
        Sorted list of unique GPU types found in the instances
    """
    gpu_types = set()

    for itype in instance_types:
        gpu_description = itype.gpu.get("description", "")
        if gpu_description and itype.gpu.get("number_of_gpus", 0) > 0:
            gpu_type = extract_gpu_type(gpu_description)
            if gpu_type:
                gpu_types.add(gpu_type)

    return sorted(list(gpu_types))


def format_gpu_display(gpu_description: str, gpu_count: int) -> str:
    """
    Format GPU information for display purposes.

    Args:
        gpu_description: The GPU description string
        gpu_count: Number of GPUs

    Returns:
        Formatted GPU display string

    Examples:
        >>> format_gpu_display("1x B300 SXM6 262GB", 1)
        "B300"
        >>> format_gpu_display("2x H100 SXM5 80GB", 2)
        "2xB300"
        >>> format_gpu_display("", 0)
        "CPU Only"
    """
    if not gpu_description or gpu_count == 0:
        return "CPU Only"

    gpu_type = extract_gpu_type(gpu_description)
    if not gpu_type:
        return "Unknown"

    if gpu_count > 1:
        return f"{gpu_count}x{gpu_type}"
    else:
        return gpu_type
