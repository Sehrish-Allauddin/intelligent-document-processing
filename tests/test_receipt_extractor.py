from pathlib import Path

from src.ocr.easy_ocr import OCRExtractor
from src.extraction.receipt_extractor import ReceiptExtractor

ocr = OCRExtractor()

extractor = ReceiptExtractor()

image = Path("datasets/business_documents/test/receipt/1.png")

results = ocr.extract(str(image))

data = extractor.extract(results)

print(data)