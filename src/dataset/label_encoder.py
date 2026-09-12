from pathlib import Path


class LabelEncoder:

    def __init__(self, dataset_path, split="train"):

        dataset_path = Path(dataset_path) / split

        self.classes = sorted(
            [
                folder.name
                for folder in dataset_path.iterdir()
                if folder.is_dir()
            ]
        )

        self.class_to_idx = {
            cls: idx
            for idx, cls in enumerate(self.classes)
        }

        self.idx_to_class = {
            idx: cls
            for cls, idx in self.class_to_idx.items()
        }

    def encode(self, label):
        return self.class_to_idx[label]

    def decode(self, idx):
        return self.idx_to_class[idx]