from zipfile import ZipFile
import os

from . import File
from ..requests import ALLOWED_IMAGE_FILES
from ..utils import allowed_file

class ZipArchive:
    def __init__(self, file):
        self.file = File.File(file)
        self.zip = ZipFile(self.file.getPath())

    def listFiles(self):
        return [file.filename for file in self.zip.infolist()]

    def listAllImages(self, extensions=ALLOWED_IMAGE_FILES):
        return [file for file in self.listFiles() if allowed_file(file, extensions)]

    def hasImages(self, extensions=ALLOWED_IMAGE_FILES):
        return len(self.listAllImages(extensions)) > 0

    def extractAll(self, path=None, members=None, pwd=None):
        self.zip.extractall(path, members, pwd)
        extractedFiles = {}
        for member in members:
            file = File.File()
            file.setPath(os.path.join(path, member))
            extractedFiles[member] = file
        return extractedFiles