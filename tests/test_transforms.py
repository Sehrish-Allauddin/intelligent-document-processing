import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.classification.dataset import BusinessDocumentDataset
from src.classification.transforms import train_transform


dataset = BusinessDocumentDataset(
    "datasets/business_documents/train",
    transform=train_transform
)

image, label = dataset[0]

print("Image Shape :", image.shape)
print("Label :", label)
print("Classes :", dataset.classes)