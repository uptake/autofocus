from pathlib import Path
from zipfile import ZipFile


def allowed_file(filename, allowed_extensions):
    """
    Check for whether a filename is in the ALLOWED_EXTENSIONS
    Args:
        filename (str): filename to check

    Returns:
        bool: whether the filename is in allowed extensions

    """
    return Path(filename).suffix.lower() in allowed_extensions


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
