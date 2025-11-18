"""Resource loading utilities for turing_display package."""

import sys
from pathlib import Path

if sys.version_info >= (3, 9):
    from importlib.resources import files
else:
    from importlib_resources import files


def get_data_path(filename: str) -> Path:
    """Get the path to a data file in the package.

    Args:
        filename: Name of the file in the data directory

    Returns:
        Path object to the data file

    Example:
        >>> from turing_display.resources import get_data_path
        >>> test_pattern = get_data_path('test_pattern.png')
        >>> # Use with PIL
        >>> from PIL import Image
        >>> img = Image.open(test_pattern)
    """
    data_dir = files('turing_display.data')
    return data_dir.joinpath(filename)


def get_data_bytes(filename: str) -> bytes:
    """Get the contents of a data file as bytes.

    Args:
        filename: Name of the file in the data directory

    Returns:
        File contents as bytes

    Example:
        >>> from turing_display.resources import get_data_bytes
        >>> data = get_data_bytes('test_pattern.png')
    """
    data_dir = files('turing_display.data')
    return data_dir.joinpath(filename).read_bytes()
