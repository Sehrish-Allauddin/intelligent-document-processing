from pathlib import Path
from PIL import Image, UnidentifiedImageError
from tqdm import tqdm


class DatasetValidator:
    """
    Validates document images before training.

    Features:
    - Detect corrupt images
    - Detect unreadable images
    - Save corrupt image list
    """

    def __init__(self):

        self.valid_images = []
        self.corrupt_images = []

    def validate(self, image_paths):

        print("\n" + "=" * 60)
        print("        VALIDATING DATASET")
        print("=" * 60)

        for image_path in tqdm(image_paths):

            try:

                with Image.open(image_path) as img:

                    img.verify()

                self.valid_images.append(image_path)

            except (UnidentifiedImageError, OSError, Exception):

                self.corrupt_images.append(image_path)

        print("\nValidation Completed")

        print(f"Valid Images   : {len(self.valid_images)}")
        print(f"Corrupt Images : {len(self.corrupt_images)}")

        return self.valid_images

    def save_report(self, output_file="corrupt_images.txt"):

        if len(self.corrupt_images) == 0:

            print("\nNo corrupt images found.")

            return

        with open(output_file, "w") as f:

            for image in self.corrupt_images:

                f.write(str(image) + "\n")

        print(f"\nReport saved -> {output_file}")
