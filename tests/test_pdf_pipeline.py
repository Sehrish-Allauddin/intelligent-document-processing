from pathlib import Path

from src.pdf.pdf_pipeline import PDFOCRPipeline
from src.ocr.text_exporter import TextExporter


resume_root = Path(
    "datasets/resumes/Resume/data"
)

pdf_file = next(
    resume_root.rglob("*.pdf")
)

print("=" * 60)
print("Testing PDF Pipeline")
print("=" * 60)

print(f"\nPDF : {pdf_file.name}\n")

pipeline = PDFOCRPipeline()

text, results = pipeline.process(
    str(pdf_file)
)

TextExporter.save_txt(
    text,
    "reports/pdf_ocr.txt"
)

TextExporter.save_json(
    results,
    "reports/pdf_ocr.json"
)

print("\nPDF OCR Completed Successfully.")