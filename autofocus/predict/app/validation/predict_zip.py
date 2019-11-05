from .validation import abort_with_errors, allowed_file, ALLOWED_ZIP_FILES


def validate_predict_zip_request(request):
    """
    Validate the given request

    Check if the request has a file and the extension is ".zip".

    Returns:
        error: Set of errors
    """
    error = {}

    file = request.files.get("file", None)
    if not file:
        error["file"] = "No file given."
    elif not allowed_file(file.filename, ALLOWED_ZIP_FILES):
        error["file"] = "File type not allowed. File must be of type {allowed}".format(
            allowed=ALLOWED_ZIP_FILES
        )

    if error:
        abort_with_errors(error)
