from pathlib import Path

import requests


def test_sample_predict_request():
    filepath = Path(__file__).resolve().parents[1] / "gallery" / "fawn.jpeg"
    response = requests.post(
        "http://0.0.0.0:8000/predict", files={"file": open(filepath, "rb")}
    )
    assert response.json()["deer"] > 0.9


def test_sample_predict_request_JPG():
    filepath = Path(__file__).resolve().parents[1] / "gallery" / "fawn.JPG"
    response = requests.post(
        "http://0.0.0.0:8000/predict", files={"file": open(filepath, "rb")}
    )
    assert response.json()["deer"] > 0.9


def test_sample_predict_zip_request():
    filepath = Path(__file__).resolve().parents[1] / "gallery.zip"
    response = requests.post(
        "http://0.0.0.0:8000/predict_zip", files={"file": open(filepath, "rb")}
    )
    assert len(response.json()) == 5
