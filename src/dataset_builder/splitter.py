import random
import shutil
from pathlib import Path


class DatasetSplitter:

    IMAGE_EXTENSIONS = {
        ".jpg",
        ".jpeg",
        ".png",
        ".bmp",
        ".tif",
        ".tiff"
    }

    def __init__(
        self,
        train_ratio=0.70,
        valid_ratio=0.15,
        test_ratio=0.15,
        seed=42
    ):
        self.train_ratio = train_ratio
        self.valid_ratio = valid_ratio
        self.test_ratio = test_ratio
        self.seed = seed

    def split_images(
        self,
        source_dir: Path,
        output_dir: Path,
        class_name: str
    ):

        print(f"\nProcessing: {source_dir}")

        images = [
            img
            for img in source_dir.rglob("*")
            if img.is_file()
            and img.suffix.lower() in self.IMAGE_EXTENSIONS
        ]

        print(f"Found {len(images)} images")

        if len(images) == 0:
            print("No images found.")
            return

        random.seed(self.seed)
        random.shuffle(images)

        total = len(images)

        train_end = int(total * self.train_ratio)
        valid_end = train_end + int(total * self.valid_ratio)

        train_images = images[:train_end]
        valid_images = images[train_end:valid_end]
        test_images = images[valid_end:]

        self.copy_images(
            train_images,
            output_dir / "train" / class_name
        )

        self.copy_images(
            valid_images,
            output_dir / "valid" / class_name
        )

        self.copy_images(
            test_images,
            output_dir / "test" / class_name
        )

        print(f"\n{class_name.upper()}")
        print(f"Train : {len(train_images)}")
        print(f"Valid : {len(valid_images)}")
        print(f"Test  : {len(test_images)}")

    def copy_images(self, images, destination):

        destination.mkdir(parents=True, exist_ok=True)

        for image in images:

            dst = destination / image.name

            if image.resolve() == dst.resolve():
                continue

            shutil.copy2(image, dst)