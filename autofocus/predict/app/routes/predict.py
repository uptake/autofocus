import time

from flask import Blueprint, jsonify, request

from ..models.File import File
from ..models.ZipArchive import ZipArchive
from ..validation.predict import validate_predict_request
from ..validation.predict_zip import validate_predict_zip_request
from ..validation.validation import abort_with_errors
from ..prediction.prediction import predict, predict_multiple


predict_route = Blueprint("predict", __name__)

@predict_route.route("/predict", methods=["POST"])
def classify_single():
    """Classify a single image"""
    # Validate request
    validate_predict_request(request)

    # Get File object
    file = File(request.files["file"])

    # Return ziped probabilities
    return jsonify(predict(file))
