from pdf2image import convert_from_path
from pathlib import Path


class PDFConverter:

    @staticmethod
    def convert(pdf_path, output_folder):

        pages = convert_from_path(pdf_path)

        image_paths = []

        for i, page in enumerate(pages):

            image_path = Path(output_folder) / f"page_{i+1}.png"

            page.save(image_path, "PNG")

            image_paths.append(image_path)

        return image_paths