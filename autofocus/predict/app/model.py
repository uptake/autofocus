from pathlib import Path

from fastai.vision import load_learner, open_image


MODEL_DIR = Path(__file__).resolve().parents[1] / "models"
MODEL_NAME = "multilabel_model_20190407.pkl"
model = load_learner(MODEL_DIR, MODEL_NAME)
CLASSES = model.data.classes


def predict_single(path):
    image = open_image(path)
    pred_classes, preds, probs = model.predict(image)
    probs = [prob.item() for prob in probs]
    return dict(zip(CLASSES, probs))


def predict_multiple(path_list):
    predictions = []
    for path in path_list:
        predictions.append(predict_single(path))
    return predictions


if __name__ == "__main__":
    test_image_path = Path(__file__).parent / "test/flower.jpeg"
    prediction = predict_single(test_image_path)
