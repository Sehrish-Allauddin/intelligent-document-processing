from pathlib import Path
import numpy as np
import torch
from PIL import Image

from src.classification.model import DocumentClassifier
from src.classification.transforms import test_transform


class Predictor:

    def __init__(
        self,
        model_path="models/best_model.pth",
        class_names=None,
        device=None,
    ):

        self.device = device or torch.device(
            "cuda" if torch.cuda.is_available() else "cpu"
        )

        self.class_names = class_names or [
            "form",
            "invoice",
            "receipt",
            "resume",
        ]

        self.model = DocumentClassifier(
            num_classes=len(self.class_names),
            pretrained=False,
        )

        self.model.load_state_dict(
            torch.load(model_path, map_location=self.device)
        )

        self.model.to(self.device)
        self.model.eval()

    def predict(self, image_path):

        image_path = Path(image_path)

        image = Image.open(image_path).convert("RGB")
        image = np.array(image)
        image = test_transform(image=image)["image"]

        image = image.unsqueeze(0).to(self.device)

        with torch.no_grad():

            outputs = self.model(image)

            probabilities = torch.softmax(outputs, dim=1)

            confidence, predicted = torch.max(
                probabilities,
                dim=1,
            )

        return {
            "class": self.class_names[predicted.item()],
            "confidence": round(confidence.item() * 100, 2),
        }