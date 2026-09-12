from pathlib import Path
import cv2


class ImageLoader:

    @staticmethod
    def load_image(image_path):

        image_path = Path(image_path)

        print("Looking for:", image_path.resolve())

        print("File exists:", image_path.exists())

        image = cv2.imread(str(image_path))

        if image is None:
            raise ValueError(f"OpenCV could not read the image: {image_path}")

        return image