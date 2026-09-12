from torch.utils.data import DataLoader

from src.classification.dataset import BusinessDocumentDataset
from src.classification.transforms import (
    train_transform,
    valid_transform,
    test_transform,
)


class DocumentDataLoader:

    def __init__(
        self,
        dataset_root="datasets/business_documents",
        batch_size=32,
        num_workers=4,
    ):

        self.train_dataset = BusinessDocumentDataset(
            f"{dataset_root}/train",
            transform=train_transform,
        )

        self.valid_dataset = BusinessDocumentDataset(
            f"{dataset_root}/valid",
            transform=valid_transform,
        )

        self.test_dataset = BusinessDocumentDataset(
            f"{dataset_root}/test",
            transform=test_transform,
        )

        self.train_loader = DataLoader(
            self.train_dataset,
            batch_size=batch_size,
            shuffle=True,
            num_workers=num_workers,
            pin_memory=True,
        )

        self.valid_loader = DataLoader(
            self.valid_dataset,
            batch_size=batch_size,
            shuffle=False,
            num_workers=num_workers,
            pin_memory=True,
        )

        self.test_loader = DataLoader(
            self.test_dataset,
            batch_size=batch_size,
            shuffle=False,
            num_workers=num_workers,
            pin_memory=True,
        )

    @property
    def classes(self):
        return self.train_dataset.classes

    @property
    def num_classes(self):
        return self.train_dataset.num_classes
    