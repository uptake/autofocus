from typing import DefaultDict

import numpy as np
from PIL import Image
from PIL.ExifTags import TAGS

from creevey.data.constants import PathOrStr


def record_exif_metadata(
    image: np.array, inpath: PathOrStr, log_dict: DefaultDict[str, dict]
):
    image = Image.open(inpath)
    pil_exif = image._getexif()
    exif = _clean_pil_exif(pil_exif)


def _clean_pil_exif(exif):
    result = {}
    for key, value in exif.items():
        decoded_key = TAGS.get(key, key)
        if decoded_key == "GPSInfo":
            value = _clean_gpsinfo(value)
        result[decoded_key] = value
    return result
