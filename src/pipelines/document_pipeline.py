import re
from pathlib import Path
import torch

from src.classification.predict import Predictor
from src.extraction.extractor_factory import ExtractorFactory
from src.extraction.resume_extractor import ResumeExtractor
from src.extraction.json_exporter import JSONExporter
from src.services.resume_ai_service import ResumeAIService


class DocumentPipeline:

    def __init__(self):

        self.device = torch.device(
            "cuda" if torch.cuda.is_available()
            else "cpu"
        )

        self.classifier = Predictor(
            model_path="models/best_model.pth",
            class_names=[
                "form",
                "invoice",
                "receipt",
                "resume",
            ],
            device=self.device,
        )

        self.resume_ai = ResumeAIService()

    # ==================================================
    # DOCUMENT TYPE VALIDATION
    # ==================================================

    @staticmethod
    def validate_document_type(predicted_type, ocr_results):

        if not isinstance(ocr_results, list):
            return predicted_type

        parts = []
        for item in ocr_results:
            if isinstance(item, dict) and item.get("text"):
                parts.append(str(item["text"]))

        text = "\n".join(parts).strip().lower()
        if not text:
            return predicted_type

        invoice_patterns = [
            r"\binvoice\b",
            r"\binvoice\s*(?:no|number|#|date|id)\b",
            r"\bbill\s*to\b",
            r"\bship\s*to\b",
            r"\bsubtotal\b",
            r"\bsub\s*total\b",
            r"\bgrand\s*total\b",
            r"\bamount\s*due\b",
            r"\btotal\s*(?:amount|payable)\b",
            r"\b(?:gst|vat|sales tax|service tax)\b",
            r"\bpayment\s*(?:method|terms|mode)\b",
            r"\bunit\s*price\b",
            r"\b(?:quantity|qty)\b",
            r"\bdescription\b",
            r"\bdue\s*date\b",
        ]

        resume_patterns = [
            r"\bwork\s+experience\b",
            r"\bprofessional\s+experience\b",
            r"\beducation\b",
            r"\bskills\b",
            r"\bprojects\b",
            r"\bcertifications?\b",
            r"\blanguages\b",
            r"\bprofessional\s+summary\b",
            r"\bcurriculum\s+vitae\b",
            r"\blinkedin\b",
            r"\bgithub\b",
            r"\bobjective\b",
        ]

        invoice_score = sum(bool(re.search(p, text, re.I)) for p in invoice_patterns)
        resume_score = sum(bool(re.search(p, text, re.I)) for p in resume_patterns)

        financial_score = sum(
            bool(re.search(p, text, re.I))
            for p in [
                r"\bsubtotal\b",
                r"\btotal\b",
                r"\bamount\b",
                r"\b(?:gst|vat|tax)\b",
                r"\bunit\s*price\b",
                r"\b(?:qty|quantity)\b",
            ]
        )

        if invoice_score >= 3 or (invoice_score >= 2 and financial_score >= 2):
            print("DOCUMENT VALIDATION: Invoice detected from OCR")
            print("Invoice signals:", invoice_score, "Financial signals:", financial_score)
            return "invoice"

        if resume_score >= 3:
            print("DOCUMENT VALIDATION: Resume detected from OCR")
            print("Resume signals:", resume_score)
            return "resume"

        return predicted_type

    # ==================================================
    # MAIN PIPELINE
    # ==================================================

    def process(
        self,
        image_path,
        ocr_results,
        output_json="data/outputs/document.json"
    ):

        image_path = Path(
            image_path
        )

        print("\n" + "=" * 60)
        print("DOCUMENT PIPELINE")
        print("=" * 60)

        # ==================================================
        # ML CLASSIFICATION
        # ==================================================

        prediction = self.classifier.predict(
            str(image_path)
        )

        predicted_type = prediction.get(
            "class",
            "unknown"
        )

        confidence = prediction.get(
            "confidence",
            0
        )

        print(
            "ML Prediction:",
            predicted_type
        )

        print(
            "ML Confidence:",
            confidence
        )

        # ==================================================
        # OCR VALIDATION
        # ==================================================

        document_type = self.validate_document_type(
            predicted_type,
            ocr_results
        )

        print(
            "FINAL Document Type:",
            document_type
        )

        print(
            "Confidence:",
            confidence
        )

        # ==================================================
        # EXTRACTOR SELECTION
        # ==================================================

        if document_type == "resume":

            print("\n" + "=" * 60)
            print("DIRECT RESUME EXTRACTOR")
            print("=" * 60)

            # Resume extractor directly
            # because resume has additional
            # ATS and AI processing.

            extractor = ResumeExtractor()

        else:

            extractor = ExtractorFactory.get(
                document_type
            )

        # --------------------------------------------------
        # Safety check
        # --------------------------------------------------

        if extractor is None:

            print(
                "WARNING: Extractor not available"
            )

            data = {
                "document_type": document_type,
                "confidence": confidence,
                "message": (
                    "Extractor not available."
                )
            }

        else:

            print(
                "Extractor:",
                extractor
            )

            print(
                "Extractor Class:",
                extractor.__class__.__name__
            )

            # ==================================================
            # EXTRACTION
            # ==================================================

            try:

                data = extractor.extract(
                    ocr_results
                )

            except Exception as e:

                print(
                    "Extraction Error:",
                    e
                )

                data = {
                    "document_type": document_type,
                    "confidence": confidence,
                    "message": str(e)
                }

        # ==================================================
        # RESUME AI
        # ==================================================

        if (
            document_type == "resume"
            and isinstance(data, dict)
        ):

            try:

                ai_result = self.resume_ai.analyze(
                    resume=data
                )

                if isinstance(
                    ai_result,
                    dict
                ):

                    data.update(
                        ai_result
                    )

            except Exception as e:

                print(
                    "Resume AI Error:",
                    e
                )

        # ==================================================
        # COMMON DATA
        # ==================================================

        if not isinstance(
            data,
            dict
        ):

            data = {}

        data["document_type"] = (
            document_type
        )

        data["confidence"] = (
            confidence
        )

        # ==================================================
        # SAVE JSON
        # ==================================================

        try:

            JSONExporter.save(
                data,
                output_json
            )

            print(
                "\nJSON Saved."
            )

        except Exception as e:

            print(
                "JSON Save Error:",
                e
            )

        # ==================================================
        # RETURN
        # ==================================================

        return data