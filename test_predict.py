import torch

from src.classification.predict import Predictor
from src.dataset.label_encoder import LabelEncoder

print("Starting Prediction Test...\n")

DATASET_PATH = "datasets/rvl_cdip/RVL-CDIP"

encoder = LabelEncoder(
    DATASET_PATH,
    split="test"
)

device = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)

predictor = Predictor(
    model_path="models/best_model.pth",
    label_encoder=encoder,
    device=device
)

image_path = "datasets/rvl_cdip/RVL-CDIP/test/invoice/2080690649.tif"

print("Predicting...\n")

label, confidence = predictor.predict(image_path)

print("\n========== RESULT ==========")
print(f"Predicted Class : {label}")
print(f"Confidence      : {confidence * 100:.2f}%")
print("============================")