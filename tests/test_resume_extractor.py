from pathlib import Path

from src.ocr.easy_ocr import OCRExtractor
from src.ocr.text_cleaner import TextCleaner
from src.extraction.resume_extractor import ResumeExtractor

# --------------------------------------------------
# Change this path to your resume file
# --------------------------------------------------

image = Path("datasets/business_documents/test/resume/3547447.jpg")    # <-- replace with your actual file

ocr = OCRExtractor()

results = ocr.extract(str(image))

results = TextCleaner.clean(results)

extractor = ResumeExtractor()

data = extractor.extract(results)

print(data)