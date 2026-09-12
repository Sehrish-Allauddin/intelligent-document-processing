from src.ocr.easy_ocr import OCRExtractor
from src.extraction.form_extractor import FormExtractor

ocr = OCRExtractor()

extractor = FormExtractor()

image = "datasets/business_documents/test/form/00836816.png"

results = ocr.extract(image)

data = extractor.extract(results)

print(data)