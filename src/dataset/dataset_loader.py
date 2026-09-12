from pathlib import Path


class DatasetLoader:

    def __init__(self, dataset_path):
        self.dataset_path = Path(dataset_path)

    def get_image_paths(self, split="test"):

        split_path = self.dataset_path / split

        extensions = [
            "*.png",
            "*.jpg",
            "*.jpeg",
            "*.tif",
            "*.tiff"
        ]

        images = []

        for ext in extensions:
            images.extend(split_path.rglob(ext))

        return images

    def summary(self):

        images = self.get_image_paths()

        print("Dataset:", self.dataset_path)
        print("Images Found:", len(images))

        return images