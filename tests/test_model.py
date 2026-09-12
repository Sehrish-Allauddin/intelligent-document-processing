import sys
from pathlib import Path

import torch

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.classification.model import DocumentClassifier


model = DocumentClassifier(
    num_classes=4
)

print(model)

dummy = torch.randn(2, 3, 224, 224)

output = model(dummy)

print()

print("Output Shape:")
print(output.shape)