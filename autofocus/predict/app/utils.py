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
    return Path(filename).suffix.lower().replace(".", "") in allowed_extensions
