from flask import Blueprint, jsonify, request

from ..filesystem.ZipArchive import ZipArchive
from ..prediction.prediction import predict_multiple
from ..validation.predict_zip import validate_predict_zip_request
from ..validation.validation import abort_with_errors


predict_zip_route = Blueprint("predict_zip", __name__)


@predict_zip_route.route("/predict_zip", methods=["POST"])
def classify_zip():
    """Classify all images from a zip file"""
    # Validate request
    validate_predict_zip_request(request)

    file = ZipArchive(request.files["file"])
    if not file.hasImages():
        error = {"file": "No image files detected in the zip file."}
        abort_with_errors(error)

    # Extract files
    files = file.extractAll(members=file.listAllImages())

    # Make prediction
    return jsonify(predict_multiple(files))
