from src.pdf.pdf_converter import PDFConverter
from src.pdf.temp_manager import TempManager

from src.ocr.easy_ocr import OCRExtractor
from src.ocr.text_cleaner import TextCleaner


class PDFOCRPipeline:

    def __init__(self):

        self.converter = PDFConverter()

        self.ocr = OCRExtractor()

        self.temp = TempManager()

    def process(self, pdf_path):

        temp_dir = self.temp.create()

        pages = self.converter.convert(
            pdf_path,
            temp_dir
        )

        if len(pages) == 0:

            raise RuntimeError(
                "No pages were generated from PDF."
            )

        first_page = pages[0]

        all_results = []

        for page in pages:

            print(f"OCR : {page.name}")

            # ------------------------------------------
            # OCR
            # ------------------------------------------

            ocr_result = self.ocr.extract(
                str(page)
            )

            # ------------------------------------------
            # IMPORTANT:
            # EasyOCR/Tesseract extractor returns a
            # dictionary. TextCleaner needs the lines.
            # ------------------------------------------

            ocr_lines = ocr_result.get(
                "lines",
                []
            )

            cleaned_lines = TextCleaner.clean(
                ocr_lines
            )

            all_results.extend(
                cleaned_lines
            )

        # ----------------------------------------------
        # Build complete text from all PDF pages
        # ----------------------------------------------

        text = TextCleaner.get_text(
            all_results
        )

        return {

            "text": text,

            "ocr_results": all_results,

            "preview_image": first_page,

            "page_count": len(pages)

        }