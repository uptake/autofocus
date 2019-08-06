import os
import time
from zipfile import ZipFile

from flask import Flask, jsonify, make_response, request
from werkzeug import secure_filename

from model import predict_multiple, predict_single
from utils import allowed_file, filter_image_files, list_zip_files

# We are going to upload the files to the server as part of the request, so set tmp folder here.
UPLOAD_FOLDER = "/tmp/"
ALLOWED_EXTENSIONS = set(["png", "jpg", "jpeg", "gif", "bmp"])

app = Flask(__name__)
app.config.from_object(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


@app.route("/predict", methods=["GET", "POST"])
def classify_single():
    """Classify a single image"""
    if request.method == "POST":
        file = request.files["file"]

        if not file:
            return "No file sent."

        filename = secure_filename(file.filename)

        if allowed_file(filename, ALLOWED_EXTENSIONS):
            file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            # this isn't super-optimal since it's saving the file to the server
            file.save(file_path)

            app.logger.info("Classifying image %s" % (file_path))

            # Get the predictions (output of the softmax) for this image
            t = time.time()
            predictions = predict_single(file_path)
            dt = time.time() - t
            app.logger.info("Execution time: %0.2f" % (dt * 1000.0))

            os.remove(file_path)

            return jsonify(predictions)
        else:
            return "File type not allowed. File must be of type {allowed}".format(
                allowed=ALLOWED_EXTENSIONS
            )


@app.route("/predict_zip", methods=["GET", "POST"])
def classify_zip():
    """Classify all images from a zip file"""
    if request.method == "POST":
        file = request.files["file"]

        if not file:
            return "No file sent."

        if not file.filename.split(".")[-1] == "zip":
            return ".zip is the only compression format currently supported"

        filename = secure_filename(file.filename)
        zip_file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(zip_file_path)

        zip_file = ZipFile(zip_file_path)
        zip_file_list = list_zip_files(zip_file_path)
        all_images = filter_image_files(zip_file_list, ALLOWED_EXTENSIONS)

        if len(all_images) == 0:
            return "No image files detected in the zip file"

        # loop through images
        start = 0
        increment = 500
        all_images_len = len(all_images)

        while start < all_images_len:
            end = start + increment
            if end > len(all_images):
                end = len(all_images)

            # extract filenames
            curr_file_list = all_images[start:end]
            for filename in curr_file_list:
                zip_file.extract(filename, path=app.config["UPLOAD_FOLDER"])

            curr_file_list = [
                os.path.join(app.config["UPLOAD_FOLDER"], x) for x in curr_file_list
            ]

            predictions = predict_multiple(curr_file_list)

            # remove files
            for curr_file in curr_file_list:
                os.remove(curr_file)

            return make_response(jsonify(predictions))

            start = end + 1


@app.route("/hello")
def hello():
    """Just a test endpoint to make sure server is running"""
    return "Hey there!\n"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
