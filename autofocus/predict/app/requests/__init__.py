ALLOWED_IMAGE_FILES = set(["png", "jpg", "jpeg", "gif", "bmp"])
ALLOWED_ZIP_FILES = {"zip"}

from .Validator import Validator

from .PredictRequestValidator import PredictRequestValidator
from .PredictZipRequestValidator import PredictZipRequestValidator
