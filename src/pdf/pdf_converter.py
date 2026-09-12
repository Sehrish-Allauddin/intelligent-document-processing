from pathlib import Path
from pdf2image import convert_from_path

from src.pdf.pdf_validator import PDFValidator


class PDFConverter:

    def __init__(
        self,
        dpi=300,
        poppler_path=None
    ):

        self.dpi = dpi
        self.poppler_path = poppler_path

    def convert(
        self,
        pdf_path,
        output_dir
    ):

        pdf_path = PDFValidator.validate(pdf_path)

        output_dir = Path(output_dir)

        output_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        pages = convert_from_path(
            pdf_path=str(pdf_path),
            dpi=self.dpi,
            poppler_path=self.poppler_path
        )

        image_paths = []

        for index, page in enumerate(pages, start=1):

            image_path = output_dir / f"page_{index}.png"

            page.save(
                image_path,
                "PNG"
            )

            image_paths.append(image_path)

        return image_paths