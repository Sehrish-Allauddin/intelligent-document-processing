from fastapi import APIRouter
from fastapi import HTTPException

from src.database.crud import DocumentCRUD
from src.services.resume_ai_service import ResumeAIService

router = APIRouter()

crud = DocumentCRUD()

service = ResumeAIService()


@router.post("/match/{document_id}")
def match_resume(

    document_id: int,

    job_description: str

):

    document = crud.get(document_id)

    if document is None:

        raise HTTPException(

            status_code=404,

            detail="Resume not found."

        )

    resume = document.json_data

    # SQLite stores JSON as string

    import json

    if isinstance(resume, str):

        resume = json.loads(resume)

    result = service.analyze(

        resume,

        job_description

    )

    return result