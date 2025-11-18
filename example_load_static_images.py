"""Example of how to use static images from the turing_display package.

This demonstrates loading bundled images that work both in development
and after the package is installed.
"""

from io import BytesIO

from PIL import Image

from turing_display.resources import get_data_bytes, get_data_path


def load_test_pattern_from_path():
    """Load the test pattern using a path object."""
    # Get the path to the bundled test pattern
    test_pattern_path = get_data_path('test_pattern_480x320.png')

    # Use it with PIL
    img = Image.open(test_pattern_path)
    print(f'Loaded image from {test_pattern_path}')
    print(f'Image size: {img.size}')
    print(f'Image mode: {img.mode}')

    return img


def load_test_pattern_from_bytes():
    """Load the test pattern using bytes."""
    # Get the raw bytes
    image_bytes = get_data_bytes('test_pattern_480x320.png')

    # Use with PIL
    img = Image.open(BytesIO(image_bytes))
    print(f'Loaded image from bytes ({len(image_bytes)} bytes)')
    print(f'Image size: {img.size}')

    return img


if __name__ == '__main__':
    print('Example 1: Loading from path')
    img1 = load_test_pattern_from_path()

    print('\nExample 2: Loading from bytes')
    img2 = load_test_pattern_from_bytes()

    # Display the image (if running in a GUI environment)
    # img1.show()
