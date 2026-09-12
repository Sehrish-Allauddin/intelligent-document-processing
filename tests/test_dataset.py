import sys
from pathlib import Path

# Add project root to Python path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.classification.dataset import BusinessDocumentDataset

dataset = BusinessDocumentDataset(
    "datasets/business_documents/train"
)

print("Classes:")
print(dataset.classes)

print("\nClass Mapping:")
print(dataset.class_to_idx)

print("\nTotal Images:")
print(len(dataset))