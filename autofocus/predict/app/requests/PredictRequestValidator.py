from . import ALLOWED_IMAGE_FILES, Validator
from ..utils import allowed_file


class PredictRequestValidator(Validator):
    """
    Validate request for endpoint predict
    """

    def validate(self):
        """
        Validate the given request

        Check if the request has a file and the extension is an allowed image extension.

        Returns:
            boolean: True if the request is valid
        """
        self.error = {}

        file = self.request.files.get('file', None)
        if not file:
            self.error['file'] = "No file given."
        elif not allowed_file(file.filename, ALLOWED_IMAGE_FILES):
            self.error['file'] = "File type not allowed. File must be of type {allowed}".format(
                allowed=ALLOWED_IMAGE_FILES
            )

        return not (self.error)
