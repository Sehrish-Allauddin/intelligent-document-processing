import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from pathlib import Path

from src.ocr.easy_ocr import OCRExtractor
from src.ocr.text_cleaner import TextCleaner
from src.ocr.text_exporter import TextExporter


invoice_folder = Path(
    "datasets/business_documents/test/invoice"
)

IMAGE = next(invoice_folder.glob("*.jpg"))

ocr = OCRExtractor()

results = ocr.extract(str(IMAGE))

results = TextCleaner.clean(results)

text = TextCleaner.get_text(results)

print(text)

TextExporter.save_txt(
    text,
    "reports/ocr.txt"
)

TextExporter.save_json(
    results,
    "reports/ocr.json"
)

print("\nOCR Finished Successfully.")