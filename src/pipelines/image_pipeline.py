from pathlib import Path

from src.ocr.easy_ocr import OCRExtractor
from src.ocr.text_cleaner import TextCleaner


class ImageOCRPipeline:

    def __init__(self):
        self.ocr = OCRExtractor()

    def process(self, image_path):

        image_path = Path(image_path)

        # OCR returns a dictionary containing:
        # text, ocr_text, lines, confidence, etc.
        ocr_result = self.ocr.extract(
            str(image_path)
        )

        # TextCleaner expects the OCR lines list,
        # not the complete OCR result dictionary.
        ocr_lines = ocr_result.get("lines", [])

        cleaned_lines = TextCleaner.clean(
            ocr_lines
        )

        text = TextCleaner.get_text(
            cleaned_lines
        )

        return {

            "text": text,

            "ocr_results": cleaned_lines,

            "preview_image": image_path,

            "page_count": 1

        }