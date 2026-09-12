import re

from src.postprocessing.ocr_corrector import OCRCorrector


class TextCleaner:
    """
    Cleans OCR output before information extraction.

    Supports both common OCR output formats:
    1. [{"text": "...", ...}, ...]
    2. ["...", "...", ...]
    """

    @staticmethod
    def clean(results):

        cleaned = []
        seen = set()

        if results is None:
            return cleaned

        # Be tolerant if an OCR engine returns a single string.
        if isinstance(results, str):
            results = [results]

        for item in results:

            # ---------------------------------
            # Normalize OCR item
            # ---------------------------------
            # Some OCR implementations return dictionaries,
            # while others return plain strings.
            if isinstance(item, dict):
                normalized_item = dict(item)
                text = normalized_item.get("text", "")
            elif isinstance(item, str):
                normalized_item = {"text": item}
                text = item
            else:
                # Ignore unexpected OCR result types safely.
                continue

            if text is None:
                continue

            text = str(text).strip()

            if not text:
                continue

            # ---------------------------------
            # Replace multiple spaces
            # ---------------------------------

            text = re.sub(
                r"\s+",
                " ",
                text
            )

            # ---------------------------------
            # Unicode cleanup
            # ---------------------------------

            text = (
                text
                .replace("\u2013", "-")
                .replace("\u2014", "-")
                .replace("\u00A0", " ")
            )

            if not text:
                continue

            # ---------------------------------
            # OCR Error Correction
            # ---------------------------------

            text = OCRCorrector.correct(text)

            if text is None:
                continue

            text = str(text).strip()

            if not text:
                continue

            # ---------------------------------
            # Remove duplicate OCR lines
            # ---------------------------------

            key = text.lower()

            if key in seen:
                continue

            seen.add(key)

            normalized_item["text"] = text
            cleaned.append(normalized_item)

        return cleaned

    @staticmethod
    def get_text(results):

        if not results:
            return ""

        lines = []

        for item in results:

            if isinstance(item, dict):
                text = item.get("text", "")
            elif isinstance(item, str):
                text = item
            else:
                continue

            if text:
                lines.append(str(text))

        text = "\n".join(lines)

        text = re.sub(
            r"\n{3,}",
            "\n\n",
            text
        )

        return text.strip()