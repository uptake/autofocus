# Image Classifier API

A flask app running on docker that allows users to post images and get predictions for a trained classifier.

The app is run with gunicorn with a proxy setup through nginx. The api runs on 127.0.0.1

## Instructions
1. Make sure docker is running
2. Build your Docker container do either of the following
    - Enter the following into the command line from the root directory:
        - `docker build -t image_api .`
        - `docker-compose build`
        - `docker-compose up`
    - `bash build.sh` (if already built, `bash run.sh`)

3. Make a request:
    - single image file:
        - `curl -F "file=@PATH_TO_FILE" -X POST http://127.0.0.1/predict`
        - `curl -F "file=@../../gallery/fawn.jpeg" -X POST http://127.0.0.1/predict`
    
    - zip file containing images:
        - `curl -F "file=@PATH_TO_FILE" -X POST http://127.0.0.1/predict_zip`
        - `curl -F "file=@./test_data/test.zip" -X POST http://127.0.0.1/predict_zip`

4. Alternatively, check out the examples in the `example_post.R` or `example_post.py` files
