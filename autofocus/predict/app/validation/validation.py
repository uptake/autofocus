import mimetypes
from pathlib import Path

from flask import abort, jsonify, make_response
from flask_api import status


ALLOWED_IMAGE_FILES = set(
    k for k, v in mimetypes.types_map.items() if v.startswith("image/")
)
ALLOWED_ZIP_FILES = {".zip"}


def abort_with_errors(error):
    """Abort with errors"""
    abort(
        make_response(
            jsonify(status=status.HTTP_400_BAD_REQUEST, error=error),
            status.HTTP_400_BAD_REQUEST,
        )
    )


def allowed_file(filename, allowed_extensions):
    """
    Check for whether a filename is in the ALLOWED_EXTENSIONS
    Args:
        filename (str): filename to check

    Returns:
        bool: whether the filename is in allowed extensions

    """
    return Path(filename).suffix.lower() in allowed_extensions
