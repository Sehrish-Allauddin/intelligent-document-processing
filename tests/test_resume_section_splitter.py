from pathlib import Path

from src.ocr.easy_ocr import OCRExtractor
from src.extraction.resume_section_splitter import ResumeSectionSplitter

ocr = OCRExtractor()

image = Path("datasets/business_documents/test/resume/3547447.jpg")   # apni resume image ka path
        
results = ocr.extract(str(image))

text = "\n".join(
    item["text"]
    for item in results
)

splitter = ResumeSectionSplitter()

sections = splitter.split(text)

for name, content in sections.items():

    print("\n" + "=" * 60)
    print(name.upper())
    print("=" * 60)
    print(content)