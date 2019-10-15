import time
from pathlib import Path
from fastai.vision import load_learner, open_image

from ..model import predict_single

MODEL_DIR = Path(__file__).resolve().parents[2] / "models"
MODEL_NAME = "multilabel_model_20190407.pkl"
model = load_learner(MODEL_DIR, MODEL_NAME)
CLASSES = model.data.classes

class Predictor:
    def predict(self, file):
        image = open_image(file.getPath())
        # Get the predictions (output of the softmax) for this image
        pred_classes, preds, probs = model.predict(image)
        self.probabilities = [prob.item() for prob in probs]

    def predict_multiple(self, files):
        predictions = {}
        for key in files:
            self.predict(files[key])
            predictions[key] = self.getProbabilities()
        return predictions


    def getProbabilities(self):
        return dict(zip(CLASSES, self.probabilities))
