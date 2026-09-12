from fastapi import FastAPI

from src.api.routes import router
from src.api.ai_routes import router as ai_router


app = FastAPI(

    title="Intelligent Document Processing API",

    version="1.0.0",

    description=(
        "Industry-Level Intelligent Document Processing System "
        "for OCR, Classification and Information Extraction."
    )

)

app.include_router(router)

app.include_router(ai_router)


@app.get("/")
def home():

    return {

        "message": "Intelligent Document Processing API",

        "status": "Running",

        "docs": "/docs"

    }