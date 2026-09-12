from pathlib import Path

from src.pipelines.document_pipeline import DocumentPipeline
from src.pipelines.image_pipeline import ImageOCRPipeline
from src.pdf.pdf_pipeline import PDFOCRPipeline
from src.pdf.temp_manager import TempManager
from src.database.crud import DocumentCRUD

class SmartDocumentPipeline:

    IMAGE_EXTENSIONS = {
        ".jpg",
        ".jpeg",
        ".png",
        ".bmp",
        ".tif",
        ".tiff"
    }

    PDF_EXTENSION = ".pdf"

    def __init__(self):

        self.image_pipeline = ImageOCRPipeline()

        self.pdf_pipeline = PDFOCRPipeline()

        self.document_pipeline = DocumentPipeline()

        self.temp = TempManager()
    
        self.crud = DocumentCRUD()

    def process(self, file_path):
        
        print("=" * 60)
        print("SMART DOCUMENT PIPELINE IS RUNNING")
        print("=" * 60)

        file_path = Path(file_path)

        extension = file_path.suffix.lower()

        print("\n" + "=" * 60)
        print("SMART DOCUMENT PIPELINE")
        print("=" * 60)

        print(f"\nInput File : {file_path.name}")

        # ------------------------------------------
        # IMAGE
        # ------------------------------------------

        if extension in self.IMAGE_EXTENSIONS:

            print("\nDetected : IMAGE")

            ocr_output = self.image_pipeline.process(file_path)

        # ------------------------------------------
        # PDF
        # ------------------------------------------

        elif extension == self.PDF_EXTENSION:

            print("\nDetected : PDF")

            ocr_output = self.pdf_pipeline.process(
                file_path
            )

        else:

            raise ValueError(
                f"Unsupported file type : {extension}"
            )

        # ------------------------------------------
        # Classification + Extraction
        # ------------------------------------------

        result = self.document_pipeline.process(
            image_path=ocr_output["preview_image"],
            ocr_results=ocr_output["ocr_results"]
        )

        result["ocr_text"] = ocr_output["text"]

        result["file_name"] = file_path.name

        result["input_type"] = extension

        result["page_count"] = ocr_output["page_count"]

        # ------------------------------------------
        # Save Document to Database
        # ------------------------------------------

        document_type = result.get("document_type", "unknown")

        confidence = result.get("confidence")

        if confidence is None:
            confidence = 0.0

        # Make JSON safely serializable
        import json

        safe_json_data = json.loads(
            json.dumps(
                result,
                default=str,
                ensure_ascii=False
            )
        )

        self.crud.create(
            file_name=file_path.name,
            document_type=document_type,
            confidence=confidence,
            raw_text=ocr_output["text"],
            json_data=safe_json_data
        )
        
        # ------------------------------------------
        # Display ATS Score (Resume Only)
        # ------------------------------------------

        if result.get("document_type") == "resume":

            print("\n" + "=" * 60)
            print("ATS RESUME SCORE")
            print("=" * 60)

            ats = result.get("ats", {})

            print(f"\nOverall Score : {ats.get('overall_score')}")

            print("\nBreakdown:")

            for key, value in ats.get("breakdown", {}).items():

                print(f"{key:<18}: {value}")

            print("\nRecommendations:")

            recommendations = ats.get("recommendations", [])

            if recommendations:

                for recommendation in recommendations:

                    print(f"- {recommendation}")

            else:

                print("No recommendations.")

        # ------------------------------------------
        # Clear Temporary PDF Images
        # ------------------------------------------

        if extension == self.PDF_EXTENSION:

            self.temp.clear()

        return result