from . import Validator, ALLOWED_IMAGE_FILES
from ..utils import allowed_file

class PredictRequestValidator(Validator):
    def validate(self):
        self.error = {}

        file = self.request.files.get('file', None)
        if not file:
            self.error['file'] = "No file given."
        elif not allowed_file(file.filename, ALLOWED_IMAGE_FILES):
            self.error['file'] = "File type not allowed. File must be of type {allowed}".format(
                allowed=ALLOWED_IMAGE_FILES
            )

        return not (self.error)
