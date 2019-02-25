import json
import numpy as np
from zipfile import ZipFile, ZipInfo


class NumpyEncoder(json.JSONEncoder):
    """ Special json encoder for numpy types """

    def default(self, obj):
        if isinstance(
            obj,
            (
                np.int_,
                np.intc,
                np.intp,
                np.int8,
                np.int16,
                np.int32,
                np.int64,
                np.uint8,
                np.uint16,
                np.uint32,
                np.uint64,
            ),
        ):
            return int(obj)
        elif isinstance(obj, (np.float_, np.float16, np.float32, np.float64)):
            return float(obj)
        elif isinstance(obj, (np.ndarray,)):  #### This is the fix
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)


def preprocess_image(img):
    pass


def allowed_file(filename, allowed_extensions):
    """
    Check for whether a filename is in the ALLOWED_EXTENSIONS
    Args:
        filename (str): filename to check

    Returns:
        bool: whether the filename is in allowed extensions

    """
    return "." in filename and filename.rsplit(".", 1)[1] in allowed_extensions


def list_zip_files(path):
    """
    List the files in a zip archive.
    Args:
        path(str): path to the zip file

    Returns:
        list of files

    """

    file = ZipFile(path)
    all_files = file.infolist()

    return [x.filename for x in all_files]


def filter_image_files(file_list, img_extensions=["jpeg", "jpg", "png", "bmp", "gif"]):
    """
    Filter the image files out of a list

    Args:
        file_list(list): list of file strings
        img_extensions(list): file extensions for image files

    Returns:

    """
    return [x for x in file_list if allowed_file(x, img_extensions)]
