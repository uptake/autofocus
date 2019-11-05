import os

from werkzeug import secure_filename


UPLOAD_FOLDER = "/tmp/"


class TemporaryFile:
    """
    Store a file and remove it upon destruction

    Parameters:
        path: The path to the file
        name: Secured filename (Can be empty)
    """

    def __init__(self, file=None, upload_path=UPLOAD_FOLDER):
        """
        Constructor of File

        Save the file on the server if a file is given.

        Parameters:
            file: Uploaded file object from flask
            upload_path: The path to upload the file
        """
        self.upload_folder = upload_path
        if file:
            self.setFromUploadedFile(file, upload_path)

    def __del__(self):
        """
        Destructor of File

        Remove the file from the server.
        """
        os.remove(self.path)

    def setFromUploadedFile(self, file, upload_path=None):
        """
        Save file from uploaded file

        Parameters:
            file: Uploaded file object from flask
            upload_path: The path to upload the file
        """
        self.name = secure_filename(file.filename)
        self.path = self.name
        if upload_path:
            self.path = os.path.join(upload_path, self.path)
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
