from flask import Blueprint, jsonify, request

from ..filesystem.TemporaryFile import TemporaryFile
from ..prediction.prediction import predict
from ..validation.predict import validate_predict_request


predict_route = Blueprint("predict", __name__)


@predict_route.route("/predict", methods=["POST"])
def classify_single():
    """Classify a single image"""
    # Validate request
    validate_predict_request(request)

    # Get File object
    file = TemporaryFile(request.files["file"])

    # Return ziped probabilities
    return jsonify(predict(file))
