# Examples of how to make requests agains the image classification endpoints
# Note:
#   1. This assumes that the image_classifier_api is running (i.e., using docker compose up)
#   2. It also assumes that the api address is at 127.0.0.1 (which should be the case)
import os

import pandas as pd
import requests


#####################
# SINGLE FILE EXAMPLE#
#####################
"""
The example below illustrates how to pass a set of files to the single
file endpoint. If you have a lot of images, this will  be a lot slower
than zipping those images into a single file and  using the predict_zip
endpoint.
"""


def allowed_file(filename, allowed_extensions):
    """
    Check for whether a filename is in the ALLOWED_EXTENSIONS

    Parameters
    ----------
    filename (str): filename to check

    Returns
    -------
    bool: whether the filename is in allowed extensions
    """
    return "." in filename and filename.rsplit(".", 1)[1] in allowed_extensions


def find_image_files(search_dir, img_extensions=["jpeg", "jpg", "png", "bmp", "gif"]):
    """
    Find all image files recursively starting in search dir

    Parameters
    ----------
    search_dir(str): path of directory to start from
    img_extensions(list): file extensions for image files

    Returns
    -------
    file_list(list): list of paths containing img_extensions
    """
    file_list = [
        os.path.join(dp, f)
        for dp, dn, fn in os.walk(os.path.expanduser(search_dir))
        for f in fn
    ]
    return [x for x in file_list if allowed_file(x, img_extensions)]


search_dir = "/Users/dacheson/repos/image-classifier-api/"
image_files = find_image_files(search_dir)

# This is the endpoint
uri = "http://127.0.0.1/predict"

# Loop through all image files and get the response
response_list = list()
for img_path in image_files:
    response = requests.post(uri, files={"file": open(img_path, "rb")})
    if response.status_code == 200:
        response_list.append(response.json())


# combine all predictions into a single data.table
predictions = pd.DataFrame(response_list)

#################
# ZipFile Example#
#################

"""
The example below illustrates how to pass a single zipfile to the
predict_zip endpoint. This will be much faster if you have a lot of
images, although therer may be some limitations on the size of the file
you send in.  Note: that the zipfile enpoint can handle directories and
subdirectories, as well as files that aren't images.
"""

uri = "http://127.0.0.1/predict_zip"
zipfile = "/Users/dacheson/repos/image-classifier-api/app/test.zip"

response = requests.post(uri, files={"file": open(zipfile, "rb")})

# response is returned as a list of objects, so just combine into a dataframe
predictions = pd.DataFrame(response.json())
