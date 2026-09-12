from pathlib import Path


class PDFValidator:

    VALID_EXTENSIONS = {".pdf"}

    @classmethod
    def validate(cls, pdf_path):

        pdf_path = Path(pdf_path)

        if not pdf_path.exists():
            raise FileNotFoundError(
                f"PDF not found : {pdf_path}"
            )

        if pdf_path.suffix.lower() not in cls.VALID_EXTENSIONS:
            raise ValueError(
                "Only PDF files are supported."
            )

        return pdf_path