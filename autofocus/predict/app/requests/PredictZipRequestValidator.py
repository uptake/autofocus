from .Validator import ALLOWED_ZIP_FILES, Validator
from ..utils import allowed_file


class PredictZipRequestValidator(Validator):
    """Validate request for endpoint predict_zip"""

    def validate(self):
        """
        Validate the given request

        Check if the request has a file and the extension is ".zip".

        Returns:
            boolean: True if the request is valid
        """
        self.error = {}

        file = self.request.files.get("file", None)
        if not file:
            self.error["file"] = "No file given."
        elif not allowed_file(file.filename, ALLOWED_ZIP_FILES):
            self.error[
                "file"
            ] = "File type not allowed. File must be of type {allowed}".format(
                allowed=ALLOWED_ZIP_FILES
            )

        return not (self.error)
