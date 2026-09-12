from pathlib import Path

from src.pipelines.smart_document_pipeline import SmartDocumentPipeline


pipeline = SmartDocumentPipeline()

print("=" * 70)
print("SMART DOCUMENT PIPELINE TEST")
print("=" * 70)

# ------------------------------------
# Test Image
# ------------------------------------

image = next(
    Path(
        "datasets/business_documents/test/invoice"
    ).glob("*.*")
)

print("\nTesting Image...\n")

result = pipeline.process(
    str(image)
)

print(result)

# ------------------------------------
# Test PDF
# ------------------------------------

pdf = next(
    Path(
        "datasets/resumes/Resume/data"
    ).rglob("*.pdf")
)

print("\nTesting PDF...\n")

result = pipeline.process(
    str(pdf)
)

print(result)