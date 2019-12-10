from pathlib import Path

from fastai.vision import load_learner, open_image


MODEL_DIR = Path(__file__).resolve().parents[2] / "models"
MODEL_NAME = "multilabel_model_20190407.pkl"
model = load_learner(MODEL_DIR, MODEL_NAME)
CLASSES = model.data.classes


def predict_multiple(files):
    """
    Predict probabilities of multiple files

    Parameters:
        files: Dict with File objects of image file

    Returns:
        dict: Dictionary of probabilities for each file in files
    """
    predictions = {}
    for key in files:
        predictions[key] = predict(files[key])
    return predictions


def predict(file):
    """
    Predict probabilities of single file

    Parameters:
        file: File object of image file
    """
    image = open_image(file.getPath())
    # Get the predictions (output of the softmax) for this image
    pred_classes, preds, probs = model.predict(image)
    return getProbabilities([prob.item() for prob in probs])


def getProbabilities(probabilities):
    """
    Return formated Probabilities

    Returns:
        dict: A dictionary of classes to probabilities
    """
    return dict(zip(CLASSES, probabilities))
