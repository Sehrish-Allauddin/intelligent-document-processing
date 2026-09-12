from fastapi import FastAPI, UploadFile, File
import shutil
import os

from src.pipelines.document_pipeline import DocumentPipeline
from src.pdf.pdf_pipeline import PDFPipeline

app = FastAPI(
    title="Intelligent Document Processing API"
)

# Image Pipeline
image_pipeline = DocumentPipeline()

# PDF Pipeline
pdf_pipeline = PDFPipeline()


@app.get("/")
def home():
    return {
        "message": "IDP API Running"
    }


@app.post("/process-document")
async def process_document(file: UploadFile = File(...)):

    temp_path = f"temp_{file.filename}"

    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        extension = os.path.splitext(file.filename)[1].lower()

        if extension == ".pdf":
            result = pdf_pipeline.process(temp_path)

        else:
            result = image_pipeline.process(temp_path)

        return result

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)