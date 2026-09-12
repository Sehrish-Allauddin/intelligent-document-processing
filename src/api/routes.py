from pathlib import Path
import shutil

from fastapi import APIRouter
from fastapi import File
from fastapi import UploadFile
from fastapi import HTTPException

from src.pipelines.smart_document_pipeline import SmartDocumentPipeline
from src.database.crud import DocumentCRUD
from src.logging.logger import logger


router = APIRouter()

pipeline = SmartDocumentPipeline()

crud = DocumentCRUD()


UPLOAD_DIR = Path("uploads")

UPLOAD_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# =====================================================
# Health Check
# =====================================================

@router.get("/health")
def health():

    return {

        "status": "Healthy",

        "service": "Intelligent Document Processing"

    }


# =====================================================
# Process Document
# =====================================================

@router.post("/process")
async def process_document(

    file: UploadFile = File(...)

):

    allowed_extensions = {

        ".jpg",
        ".jpeg",
        ".png",
        ".bmp",
        ".tif",
        ".tiff",
        ".pdf"

    }

    extension = Path(
        file.filename
    ).suffix.lower()

    if extension not in allowed_extensions:

        raise HTTPException(

            status_code=400,

            detail="Unsupported file type."

        )

    file_path = UPLOAD_DIR / file.filename

    with open(
        file_path,
        "wb"
    ) as buffer:

        shutil.copyfileobj(
            file.file,
            buffer
        )

    # ---------------------------------------
    # Log Uploaded File
    # ---------------------------------------

    logger.info(
        f"Uploaded file: {file.filename}"
    )

    # ---------------------------------------
    # Process Document
    # ---------------------------------------

    result = pipeline.process(
        str(file_path)
    )

    # ---------------------------------------
    # Log Processing Result
    # ---------------------------------------

    logger.info(
        f"Processed {file.filename} "
        f"as {result.get('document_type')}"
    )

    # ---------------------------------------
    # Save Result into Database
    # ---------------------------------------

    crud.create(

        file_name=file.filename,

        document_type=result.get("document_type"),

        confidence=result.get("confidence"),

        raw_text=result.get("ocr_text"),

        json_data=result

    )

    return result


# =====================================================
# Get All Documents
# =====================================================

@router.get("/documents")
def get_documents():

    documents = crud.get_all()

    results = []

    for doc in documents:

        results.append({

            "id": doc.id,

            "file_name": doc.file_name,

            "document_type": doc.document_type,

            "confidence": doc.confidence

        })

    return results


# =====================================================
# Get Document By ID
# =====================================================

@router.get("/documents/{document_id}")
def get_document(document_id: int):

    document = crud.get(document_id)

    if document is None:

        raise HTTPException(

            status_code=404,

            detail="Document not found."

        )

    return {

        "id": document.id,

        "file_name": document.file_name,

        "document_type": document.document_type,

        "confidence": document.confidence,

        "raw_text": document.raw_text,

        "json_data": document.json_data

    }


# =====================================================
# Search Documents By Type
# =====================================================

@router.get("/documents/type/{document_type}")
def search_documents(document_type: str):

    documents = crud.get_by_type(
        document_type
    )

    results = []

    for doc in documents:

        results.append({

            "id": doc.id,

            "file_name": doc.file_name,

            "document_type": doc.document_type,

            "confidence": doc.confidence

        })

    return results


# =====================================================
# Delete Document
# =====================================================

@router.delete("/documents/{document_id}")
def delete_document(document_id: int):

    deleted = crud.delete(document_id)

    if not deleted:

        raise HTTPException(

            status_code=404,

            detail="Document not found."

        )

    return {

        "message": "Document deleted successfully."

    }