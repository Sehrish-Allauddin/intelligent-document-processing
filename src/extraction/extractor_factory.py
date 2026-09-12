from src.extraction.invoice_extractor import InvoiceExtractor
from src.extraction.resume_extractor import ResumeExtractor
from src.extraction.receipt_extractor import ReceiptExtractor
from src.extraction.form_extractor import FormExtractor

print("LOADING NEW RESUME EXTRACTOR")

class ExtractorFactory:

    _extractors = {

    "invoice": InvoiceExtractor(),

    "receipt": ReceiptExtractor(),

    "resume": ResumeExtractor(),

    "form": FormExtractor()

}

    @classmethod
    def get(cls, document_type):

        if document_type is None:
            return None

        return cls._extractors.get(
            str(document_type).strip().lower()
        )