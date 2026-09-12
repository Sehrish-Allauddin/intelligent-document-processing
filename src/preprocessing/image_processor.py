import cv2


class ImageProcessor:

    @staticmethod
    def grayscale(image):
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    @staticmethod
    def resize(image, scale=2):
        h, w = image.shape[:2]
        return cv2.resize(image, (w * scale, h * scale))

    @staticmethod
    def remove_noise(image):
        return cv2.fastNlMeansDenoising(image)

    @staticmethod
    def enhance_contrast(image):
        clahe = cv2.createCLAHE(
            clipLimit=2.0,
            tileGridSize=(8, 8)
        )
        return clahe.apply(image)

    @staticmethod
    def sharpen(image):

        kernel = [
            [0, -1, 0],
            [-1, 5, -1],
            [0, -1, 0]
        ]

        import numpy as np

        kernel = np.array(kernel)

        return cv2.filter2D(image, -1, kernel)

    @staticmethod
    def threshold(image):

        return cv2.adaptiveThreshold(
            image,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            31,
            11,
        )

    @staticmethod
    def save(image, output_path):

        cv2.imwrite(str(output_path), image)