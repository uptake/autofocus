import time

from flask import Flask, jsonify, request

from .models.File import File
from .models.Predictor import Predictor
from .models.ZipArchive import ZipArchive
from .requests.PredictRequestValidator import PredictRequestValidator
from .requests.PredictZipRequestValidator import PredictZipRequestValidator

# We are going to upload the files to the server as part of the request, so set tmp folder here.
UPLOAD_FOLDER = "/tmp/"

app = Flask(__name__)
app.config.from_object(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


@app.route("/predict", methods=["POST"])
def classify_single():
    """Classify a single image"""
    # Validate request
    validator = PredictRequestValidator(request)
    if not validator.validate():
        validator.abort()

    # Get File object
    file = File(request.files["file"], app.config["UPLOAD_FOLDER"])

    # Predict probabilities
    app.logger.info("Classifying image %s" % (file.getPath()))
    t = time.time()
    predictor = Predictor()
    predictor.predict(file)
    dt = time.time() - t
    app.logger.info("Execution time: %0.2f" % (dt * 1000.0))

    # Return ziped probabilities
    return jsonify(predictor.getProbabilities())


@app.route("/predict_zip", methods=["POST"])
def classify_zip():
    """Classify all images from a zip file"""
    # Validate request
    validator = PredictZipRequestValidator(request)
    if not validator.validate():
        validator.abort()

    file = ZipArchive(request.files["file"], app.config["UPLOAD_FOLDER"])
    if not file.hasImages():
        validator.error['file'] = "No image files detected in the zip file."
        validator.abort()

    # Extract files
    files = file.extractAll(app.config["UPLOAD_FOLDER"], file.listAllImages())

    # Make prediction
    predictor = Predictor()
    return jsonify(predictor.predict_multiple(files))


@app.route("/hello")
def hello():
    """Just a test endpoint to make sure server is running"""
    return "Hey there!\n"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
