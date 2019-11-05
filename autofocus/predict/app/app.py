import time

from flask import Flask, jsonify, request

from .models.File import File
from .models.ZipArchive import ZipArchive
from .validation.predict import validate_predict_request
from .validation.predict_zip import validate_predict_zip_request
from .validation.validation import abort_with_errors
from .prediction.prediction import predict, predict_multiple


# We are going to upload the files to the server as part of the request, so set tmp folder here.
UPLOAD_FOLDER = "/tmp/"

app = Flask(__name__)
app.config.from_object(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


@app.route("/predict", methods=["POST"])
def classify_single():
    """Classify a single image"""
    # Validate request
    validate_predict_request(request)

    # Get File object
    file = File(request.files["file"], app.config["UPLOAD_FOLDER"])

    # Return ziped probabilities
    return jsonify(predict(file))


@app.route("/predict_zip", methods=["POST"])
def classify_zip():
    """Classify all images from a zip file"""
    # Validate request
    validate_predict_zip_request(request)

    file = ZipArchive(request.files["file"], app.config["UPLOAD_FOLDER"])
    if not file.hasImages():
        error = {
            "file": "No image files detected in the zip file."
        }
        abort_with_errors(error)

    # Extract files
    files = file.extractAll(app.config["UPLOAD_FOLDER"], file.listAllImages())

    # Make prediction
    return jsonify(predict_multiple(files))


@app.route("/hello")
def hello():
    """Just a test endpoint to make sure server is running"""
    return "Hey there!\n"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
