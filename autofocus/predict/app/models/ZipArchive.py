import os
from zipfile import ZipFile
from .File import File
from ..requests.Validator import ALLOWED_IMAGE_FILES
from ..utils import allowed_file


class ZipArchive:
    """
    Archive of a zip file

    This class is to store and access a zip file.

    Parameters:
        file: The storage of the zip file (gets removed from the os upon destructor call)
        zip: Opened zip file
    """

    def __init__(self, file, upload_folder=None):
        """
        Constructor of ZipFile

        Store the given file and open the zip file.

        Parameters:
            file: Uploaded file from flask
            upload_folder: The folder to save the zip file
        """
        self.file = File(file, upload_folder)
        self.zip = ZipFile(self.file.getPath())

    def listFiles(self):
        """
        List all files in the zip

        Returns:
            array: Array of filenames
        """
        return [file.filename for file in self.zip.infolist()]

    def listAllImages(self, extensions=ALLOWED_IMAGE_FILES):
        """
        List all image files

        Lists all image files within the zip archive based on the given extensions

        Parameters:
            extensions: Array of allowed image extensions
        
        Returns:
            array: Array of filenames matching the extension
        """
        return [file for file in self.listFiles() if allowed_file(file, extensions)]

    def hasImages(self, extensions=ALLOWED_IMAGE_FILES):
        """
        Check for images in the zip file

        Parameters:
            extensions: Array of allowed image extensions
        
        Returns:
            boolean: True if zip has images
        """
        return len(self.listAllImages(extensions)) > 0

    def extractAll(self, path=None, members=None):
        """
        Extract all the given files

        Extractes all the given files and stores them as File objects.
        Upon destruction of the array, files are getting removed from os.

        Parameters:
            path: Path to store files
            members: Files to extract
        
        Returns:
            array: Array of extracted File objects 
        """
        self.zip.extractall(path, members)
        extractedFiles = {}
        for member in members:
            file = File()
            file.setPath(os.path.join(path, member))
            extractedFiles[member] = file
        return extractedFiles
