"""Preprocess images.
"""
import argparse
import logging
import os
import psutil
import time

from collections import defaultdict
from datetime import datetime
from os.path import abspath
from pathlib import Path
from typing import List, Union

import cv2 as cv
import numpy as np
import pandas as pd

from PIL import Image
from PIL.ExifTags import TAGS
from tqdm import tqdm

from autofocus.util import write_csv


MAX_FOOTER_LENGTH = 198
MIN_DIM = 256


def main(indir: str,
         outdir: str,
         extensions: List[str],
         ) -> None:
    image_properties = defaultdict(list)
    image_paths = get_paths_with_extensions(indir, extensions)
    for path in tqdm(image_paths):
        image = cv.imread(str(path))
        try:
            processed_image = _process_image(image)
        except (ZeroDivisionError, TypeError):
            logging.warning(f'Skipping {path}, which did not load properly.')
        else:
            outpath = abspath(path).replace(abspath(indir), abspath(outdir))
            _record_properties(processed_image, image_properties, path, outpath)
            save_image(processed_image, outpath)
    csv_outpath = Path(outdir) / 'image_properties.csv'
    write_csv(pd.DataFrame(image_properties), csv_outpath)


def get_paths_with_extensions(directory: Union[str, Path], extensions: List[str]) -> List[Path]:
    """Get a list of the path to every file recursively contained within
    `directory` whose name ends with one of the specified extensions.
    """
    image_paths = []
    for dir, _, files in os.walk(directory):
        for filename in files:
            if any(filename.endswith(ext) for ext in extensions):
                image_paths.append(Path(dir, filename))
    return image_paths


def _process_image(image: np.array) -> np.array:
    image = trim_bottom(image, MAX_FOOTER_LENGTH)
    image = resize_to_min_dim(image, min_dim=MIN_DIM)
    return image


def trim_bottom(image: np.array, num_rows: int) -> np.array:
    """Remove bottom num_rows rows of pixels from image
    """
    return image[:-num_rows, ...]


def resize_to_min_dim(image: np.array, min_dim: int) -> np.array:
    """Resize an image so that its smaller spatial dimension has the
        specified length

    Args:
        image: NumPy array representing a 2D image, with the vertical
            and horizontal spatial dimensions as its first two axes
        min_dim: Desired length for the *shorter* of the two spatial
            dimensions

    Returns:
        Input image resized to have min_dim as the shorter of its two
            spatial dimensions.
    """
    shape_dims = image.shape[:2]
    min_dim_now, max_dim_now = sorted(shape_dims)
    aspect_ratio = max_dim_now/min_dim_now
    max_dim = int(min_dim*aspect_ratio)
    outshape = (min_dim, max_dim) if shape_dims[0] == min_dim_now else (max_dim, min_dim)
    return cv.resize(image, outshape[::-1]) # cv.resize takes shape width-first


def _record_properties(image: np.array, image_properties: dict, inpath: Path, outpath: Path) -> None:
    image_properties['filepath'].append(str(outpath))

    is_night = 1 if has_channels_equal(image) else 0
    image_properties['night'].append(is_night)

    grayscale_image = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    mean_brightness = grayscale_image.mean()
    image_properties['mean_brightness'].append(mean_brightness)

    image_properties['exif_timestamp'].append(get_timestamp(get_exif(inpath)))


def get_exif(path: str) -> dict:
    """Get Exif metadata from image

    Args:
        path: Path to image file that contains Exif metadata (.tiff or
            .jpeg)

    Returns:
        Dictionary of Exif metadata contents
    """
    image = Image.open(path)
    pil_exif = image._getexif()
    return _clean_pil_exif(pil_exif)


def _clean_pil_exif(exif):
    result = {}
    for key, value in exif.items():
        decoded_key = TAGS.get(key, key)
        if decoded_key == 'GPSInfo':
            value = _clean_gpsinfo(value)
        result[decoded_key] = value
    return result


def get_timestamp(exif: dict) -> datetime:
    """Get timestamp from Exif metadata as a datetime object

    Args:
        exif: dictionary of Exif metadata that includes "DateTime"
    """
    timestamp = exif['DateTime']
    timestamp = datetime.strptime(timestamp, '%Y:%m:%d %H:%M:%S')
    return timestamp


def has_channels_equal(image: np.array) -> bool:
    """Indicates whether all channels have equal values.

    Assumes that channels lie along the final axis.

    Args:
        image: NumPy array

    Returns:
        True if all channels have equal values, including when there is
            only one channel as long as there is an axis corresponding
            to that channel (e.g. a grayscale image with shape height
            x width x 1, but not one with shape height x width)
    """
    first_channel = image[..., 0]
    return all(
        [np.equal(image[..., channel_num], first_channel).all()
         for channel_num in range(1, image.shape[-1])
         ]
    )


def save_image(image: np.array, outpath: Path) -> None:
    """Writes `image` to `outpath`.

    Creates directory for `outpath` if it doesn't exist. If a file
    already exists at `outpath`, log a warning and do not overwrite it.
    """
    outdir = os.path.dirname(outpath)
    if not os.path.isdir(outdir):
        os.makedirs(outdir)
    if os.path.isfile(outpath):
        logging.warning(f'{outpath} already exists. Skipping save.')
    else:
        logging.debug(f'Saving image to {outpath}')
        cv.imwrite(str(outpath), image)


def _parse_args() -> dict:
    """Parse command-line arguments, and log them with level INFO.

    Also provides file docstring as description for --help/-h.

    Returns:
        Command-line argument names and values as keys and values of a
            Python dictionary
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--indir', '-i',
                        type=str,
                        required=True,
                        help='Path to directory that recursively contains '
                             'image files referred to by the files '
                             'specified in detections_inpaths.'
                        )
    parser.add_argument('--outdir', '-o',
                        type=str,
                        required=True,
                        help='Path to directory to hold cleaned images.'
                        )
    parser.add_argument('--extensions', '-e',
                        nargs='*',
                        required=False,
                        help='File extensions on image files, without "."',
                        default='JPG'
                        )
    args = vars(parser.parse_args())
    logging.info(f'Arguments pass at command line: {args}')
    return args


def _log_memory() -> None:
    memory = psutil.virtual_memory()
    logging.info(f'Memory total:  {_convert_to_gb(memory.total)} GB')
    logging.info(f'Memory used:  {_convert_to_gb(memory.used)} GB')
    logging.info(f'Memory available:  {_convert_to_gb(memory.available)} GB')


def _convert_to_gb(bytes: float) -> float:
    return round(bytes / (2**30), 2)


if __name__ == '__main__':
    start_time = time.time()
    logging.basicConfig(format='%(levelname)s %(asctime)s %(message)s')
    logging.getLogger().setLevel(logging.INFO)
    args_dict = _parse_args()
    _log_memory()

    main(**args_dict)

    _log_memory()
    end_time = time.time()
    logging.info(f'Completed in {round(end_time - start_time, 2)} seconds')
