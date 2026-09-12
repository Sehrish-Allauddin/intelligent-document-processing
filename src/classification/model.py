import timm
import torch.nn as nn


class DocumentClassifier(nn.Module):
    """
    EfficientNet-B0 based document classifier.
    """

    def __init__(
        self,
        num_classes: int = 4,
        pretrained: bool = True,
    ):
        super().__init__()

        self.model = timm.create_model(
            "efficientnet_b0",
            pretrained=pretrained,
        )

        in_features = self.model.classifier.in_features

        self.model.classifier = nn.Linear(
            in_features,
            num_classes
        )

    def forward(self, x):
        return self.model(x)