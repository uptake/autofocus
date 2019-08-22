from pathlib import Path

import requests

BASE_URL = "http://localhost:8000"


def test_sample_predict_request():
    filepath = Path(__file__).resolve().parents[1] / "gallery" / "fawn.jpeg"
    response = requests.post(
        f"{BASE_URL}/predict", files={"file": open(filepath, "rb")}
    )
    assert response.json()["deer"] > 0.9


def test_sample_predict_request_JPG():
    filepath = Path(__file__).resolve().parents[1] / "gallery" / "fawn.JPG"
    response = requests.post(
        f"{BASE_URL}/predict", files={"file": open(filepath, "rb")}
    )
    assert response.json()["deer"] > 0.9


def test_sample_predict_zip_request():
    filepath = Path(__file__).resolve().parents[1] / "gallery.zip"
    response = requests.post(
        f"{BASE_URL}/predict_zip", files={"file": open(filepath, "rb")}
    )
    assert len(response.json()) == 5
