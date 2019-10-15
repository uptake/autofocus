import os
from werkzeug import secure_filename
from ..app import app

class File:
    def __init__(self, file=None):
        if file:
            self.setFromUploadedFile(file)

    def __del__(self):
        os.remove(self.path)

    def setFromUploadedFile(self, file):
        self.name = secure_filename(file.filename)
        self.path = os.path.join(app.config["UPLOAD_FOLDER"], self.name)
        file.save(self.path)

    def setPath(self, path):
        self.path = path

    def getPath(self):
        return self.path
