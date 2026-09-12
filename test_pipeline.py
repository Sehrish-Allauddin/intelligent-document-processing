print("Starting Pipeline Test...")
from src.pipelines.document_pipeline import DocumentPipeline
print("Import Successful")
pipeline = DocumentPipeline()
print("Pipeline Created")
result = pipeline.process(
    "datasets/rvl_cdip/RVL-CDIP/test/invoice/0000023361.tif"
)

print("\nFinal Output:")
print(result)