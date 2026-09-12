from pathlib import Path
from typing import Optional

import numpy as np
from PIL import Image

from torch.utils.data import Dataset
from torchvision.datasets import ImageFolder


class BusinessDocumentDataset(Dataset):
    """
    Business Document Classification Dataset
    """

    def __init__(
        self,
        root_dir: str | Path,
        transform: Optional[callable] = None,
    ):

        self.dataset = ImageFolder(root=root_dir)

        self.transform = transform

        self.classes = self.dataset.classes
        self.class_to_idx = self.dataset.class_to_idx

    def __len__(self):

        return len(self.dataset)

    def __getitem__(self, index):

        image_path, label = self.dataset.samples[index]

        image = Image.open(image_path).convert("RGB")

        image = np.array(image)

        if self.transform is not None:

            image = self.transform(image=image)["image"]

        return image, label

    @property
    def num_classes(self):

        return len(self.classes)