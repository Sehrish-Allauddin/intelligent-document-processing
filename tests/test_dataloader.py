import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.classification.dataloader import DocumentDataLoader

loader = DocumentDataLoader(
    batch_size=8,
    num_workers=0   # Windows ke liye testing me 0
)

print("Classes:")
print(loader.classes)

print()

print("Number of Classes:")
print(loader.num_classes)

print()

images, labels = next(iter(loader.train_loader))

print("Image Batch Shape:", images.shape)
print("Label Shape:", labels.shape)
print("Labels:", labels)