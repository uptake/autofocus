import os
from werkzeug import secure_filename
from ..app import app

class File:
    def __init__(self, file):
        self.name = secure_filename(file.filename)
        self.path = os.path.join(app.config["UPLOAD_FOLDER"], self.name)
        file.save(self.path)

    def __del__(self):
        os.remove(self.path)

    def getPath(self):
        return self.path
