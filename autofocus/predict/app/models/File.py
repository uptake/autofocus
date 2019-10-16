import os
from werkzeug import secure_filename
from ..app import app


class File:
    """
    Store a file and remove it upon destruction

    Parameters:
        path: The path to the file
        name: Secured filename (Can be empty)
    """

    def __init__(self, file=None):
        """
        Constructor of File

        Save the file on the server if a file is given.

        Parameters:
            file: Uploaded file object from flask
        """
        if file:
            self.setFromUploadedFile(file)

    def __del__(self):
        """
        Destructor of File

        Remove the file from the server.
        """
        os.remove(self.path)

    def setFromUploadedFile(self, file):
        """
        Save file from uploaded file

        Parameters:
            file: Uploaded file object from flask
        """
        self.name = secure_filename(file.filename)
        self.path = os.path.join(app.config["UPLOAD_FOLDER"], self.name)
        file.save(self.path)

    def setPath(self, path):
        """
        Set the path to a saved file

        Parameters:
            path: Path to the file
        """
        self.path = path

    def getPath(self):
        """
        Return the saved path

        Returns:
            string: Path to the file
        """
        return self.path
