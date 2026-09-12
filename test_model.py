import torch

from src.classification.model import DocumentClassifier

model = DocumentClassifier(num_classes=16)

dummy = torch.randn(4, 3, 224, 224)

output = model(dummy)

print(output.shape)