from typing import Iterator, Literal, Tuple

import numpy as np
import numpy.typing as npt
from PIL import Image

# ruff: noqa: N802 # RGB565/BGR/BGRA are abreviations so should be capitalized


def serialized_chunk(data: bytes, chunk_size: int) -> Iterator[bytes]:
    for i in range(0, len(data), chunk_size):
        yield data[i : i + chunk_size]


def image_to_RGB565(image: Image.Image, endianness: Literal['big', 'little']) -> bytes:
    if image.mode not in ['RGB', 'RGBA']:
        # we need the first 3 channels to be R, G and B
        image = image.convert('RGB')

    rgb: npt.NDArray[np.uint8] = np.asarray(image)

    # flatten the first 2 dimensions (width and height) into a single RGB stream
    rgb = rgb.reshape((image.size[1] * image.size[0], -1))

    # extract R, G, B channels and promote them to 16 bits
    r = rgb[:, 0].astype(np.uint16)
    g = rgb[:, 1].astype(np.uint16)
    b = rgb[:, 2].astype(np.uint16)

    # construct RGB565
    r = r >> 3
    g = g >> 2
    b = b >> 3
    rgb565 = (r << 11) | (g << 5) | b

    # serialize to the correct endianness
    typ = '>u2' if endianness == 'big' else '<u2'
    return rgb565.astype(typ).tobytes()


def image_to_BGR(image: Image.Image) -> Tuple[bytes, int]:
    if image.mode not in ['RGB', 'RGBA']:
        # we need the first 3 channels to be R, G and B
        image = image.convert('RGB')
    rgb: npt.NDArray[np.uint8] = np.asarray(image)
    # same as rgb[:, :, [2, 1, 0]] but faster
    bgr: npt.NDArray[np.uint8] = np.take(rgb, (2, 1, 0), axis=-1)
    return bgr.tobytes(), 3


def image_to_BGRA(image: Image.Image) -> Tuple[bytes, int]:
    if image.mode != 'RGBA':
        image = image.convert('RGBA')
    rgba: npt.NDArray[np.uint8] = np.asarray(image)
    # same as rgba[:, :, [2, 1, 0, 3]] but faster
    bgra: npt.NDArray[np.uint8] = np.take(rgba, (2, 1, 0, 3), axis=-1)
    return bgra.tobytes(), 4


def image_to_compressed_BGRA(image: Image.Image) -> Tuple[bytes, int]:
    # TODO: optimize like other functions above
    image_data = image.convert('RGBA').load()
    if image_data is None:
        msg = f'Failed to load image data from {image}'
        raise InvalidImageError(msg)
    compressed_bgra = _compress_to_BGRA(image)
    return bytes(compressed_bgra), 3


def _compress_to_BGRA(image: Image.Image) -> bytearray:
    """Compress a PIL Image into compressed BGRA format.

    Each pixel (RGBA => 4 bytes, 32 bits) is represented by:
        * 4 bits for alfa
        * 6 bits for blue
        * 6 bits for green
        * 8 bits for red
    3 bytes (24 bits) per pixel for a total compression of 25%.

    The bytestream contains:
    * 6 upper bits of blue
    * bit 7 and 6 of alpha (upper two bits)
    * 6 upper bits of green
    * bit 5 and 4 of alpha
    * 8 bits of red

    Args:
        image (Image.Image): Source image

    Raises:
        InvalidImageError: if the source returns no data when converted to RGBA

    Returns:
        bytearray: Compressed image data
    """
    compressed_bgra = bytearray()
    image_data = image.convert('RGBA').load()
    if image_data is None:
        msg = f'Failed to load image data from {image}'
        raise InvalidImageError(msg)
    for h in range(image.height):
        for width in range(image.width):
            pixel = image_data[width, h]
            # pixel is now [r, g, b, a],
            a = pixel[3] >> 4  # downsample alpha to 4 bits
            compressed_bgra.append(pixel[2] & 0xFC | a >> 2)
            compressed_bgra.append(pixel[1] & 0xFC | a & 2)
            compressed_bgra.append(pixel[0])
    return compressed_bgra
