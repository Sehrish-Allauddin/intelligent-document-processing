"""
Robust generic OCR engine for IDP.

Tesseract is the primary engine. EasyOCR is only a fallback.
The engine selects the best Tesseract pass instead of merging noisy
outputs from different preprocessing variants.
"""
from __future__ import annotations

from email.mime import image
import os
import re
from typing import Any, Dict, List, Tuple
import cv2
import numpy as np
from PIL import Image
from scipy import io


class OCRExtractor:
    def __init__(self, languages: List[str] | None = None, gpu: bool = True):
        self.languages = languages or ["en"]
        self.gpu = gpu
        self.easy_reader = None
        self._easyocr_initialized = False
        self.tesseract_available = False
        self._configure_tesseract()

    def _configure_tesseract(self) -> None:
        try:
            import pytesseract
        except ImportError:
            print("pytesseract : not installed")
            return

        candidates = [
            os.environ.get("TESSERACT_CMD", ""),
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        ]
        for path in candidates:
            if not path:
                continue
            if path and os.path.exists(path):
                pytesseract.pytesseract.tesseract_cmd = path
                break

        try:
            version = pytesseract.get_tesseract_version()
            self.tesseract_available = True
            print(f"Tesseract : available ({version})")
        except Exception as exc:
            print(f"Tesseract : not available ({exc})")

    def _init_easyocr(self) -> bool:
        if self._easyocr_initialized:
            return self.easy_reader is not None
        self._easyocr_initialized = True
        try:
            import easyocr
            print("Initializing EasyOCR fallback")
            self.easy_reader = easyocr.Reader(self.languages, gpu=self.gpu, verbose=False)
            return True
        except Exception as exc:
            print(f"EasyOCR initialization failed: {exc}")
            return False

    def _to_numpy(self, image):
       """
       Convert different image input types into a numpy RGB image.

       Supports:
       - numpy.ndarray
       - PIL.Image.Image
       - Streamlit UploadedFile
       - bytes / bytearray
       - file-like objects
       - image file paths
       """

       # ------------------------------------------
       # 1. Already numpy array
       # ------------------------------------------
       if isinstance(image, np.ndarray):
          if image.size == 0:
              raise ValueError("Image numpy array is empty.")

          return image

        # ------------------------------------------
        # 2. PIL Image
        # ------------------------------------------
       if isinstance(image, Image.Image):
          return np.array(image.convert("RGB"))

        # ------------------------------------------
        # 3. Bytes / bytearray
        # ------------------------------------------
       if isinstance(image, (bytes, bytearray)):
          try:
              pil_image = Image.open(io.BytesIO(image))
              return np.array(pil_image.convert("RGB"))
          except Exception as e:
              raise TypeError(
                  f"Could not decode image bytes: {e}"
                )

        # ------------------------------------------
        # 4. Streamlit UploadedFile
        # ------------------------------------------
       if hasattr(image, "getvalue"):
          try:
              data = image.getvalue()

              if data:
                  pil_image = Image.open(io.BytesIO(data))
                  return np.array(pil_image.convert("RGB"))

          except Exception:
              pass

        # ------------------------------------------
        # 5. File-like object
        # ------------------------------------------
       if hasattr(image, "read"):
          try:
              image.seek(0)
          except Exception:
              pass

          try:
             data = image.read()

             if data:
                 pil_image = Image.open(io.BytesIO(data))
                 return np.array(pil_image.convert("RGB"))

          except Exception:
              pass

        # ------------------------------------------
        # 6. File path
        # ------------------------------------------
       if isinstance(image, (str, os.PathLike)):
           path = os.fspath(image)

           if os.path.exists(path):
            try:
                pil_image = Image.open(path)
                return np.array(pil_image.convert("RGB"))
            except Exception as e:
                raise TypeError(
                    f"Could not open image file '{path}': {e}"
                )

        # ------------------------------------------
        # 7. Unsupported type
        # ------------------------------------------
       raise TypeError(
          "Unsupported image type: "
          f"{type(image).__name__}. "
          "Expected numpy array, PIL Image, bytes, "
          "Streamlit UploadedFile, file-like object, or image path."
        )

    def _variants(self, image: np.ndarray) -> List[Tuple[str, np.ndarray]]:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        h, w = gray.shape
        scale = 2.0 if max(h, w) < 2400 else 1.5
        up = cv2.resize(gray, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
        # Improve local contrast without destroying character strokes.
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8)).apply(up)
        _, otsu = cv2.threshold(clahe, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        adaptive = cv2.adaptiveThreshold(
            clahe, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, 31, 11
        )
        return [
            ("original", image),
            ("gray", gray),
            ("upscaled", up),
            ("clahe", clahe),
            ("otsu", otsu),
            ("adaptive", adaptive),
        ]

    def _tesseract_pass(self, image: np.ndarray, psm: int) -> List[Dict[str, Any]]:
        if not self.tesseract_available:
            return []
        import pytesseract
        config = f"--oem 3 --psm {psm}"
        try:
            data = pytesseract.image_to_data(
                image, lang="eng", config=config,
                output_type=pytesseract.Output.DICT
            )
        except Exception as exc:
            print(f"Tesseract OCR warning: {exc}")
            return []

        groups: Dict[Tuple[int, int, int], List[Tuple[int, str, float]]] = {}
        total = len(data.get("text", []))
        for i in range(total):
            text = str(data["text"][i]).strip()
            if not text:
                continue
            try:
                conf = float(data["conf"][i])
            except Exception:
                conf = 0.0
            key = (
                int(data["block_num"][i]),
                int(data["par_num"][i]),
                int(data["line_num"][i]),
            )
            groups.setdefault(key, []).append((int(data["left"][i]), text, conf))

        out = []
        for words in groups.values():
            words.sort(key=lambda x: x[0])
            text = " ".join(x[1] for x in words).strip()
            if text:
                out.append({
                    "text": text,
                    "confidence": round(sum(x[2] for x in words) / len(words), 2),
                    "engine": "tesseract",
                    "psm": psm,
                })
        return out

    @staticmethod
    def _clean(text: str) -> str:
        text = str(text or "").replace("\u00a0", " ")
        text = re.sub(r"[ \t]+", " ", text)
        return text.strip()

    def _score(self, lines: List[Dict[str, Any]]) -> float:
        text = "\n".join(x["text"] for x in lines)
        low = text.lower()
        score = 0.0
        score += min(len(lines), 80) * 0.15
        score += sum(float(x.get("confidence", 0)) for x in lines) / max(len(lines), 1) * 0.35
        for term, weight in [
            ("subtotal", 12), ("total", 8), ("tax", 5), ("change", 5),
            ("items sold", 8), ("receipt", 5), ("rcpt", 5), ("walmart", 4),
            ("cash", 3), ("debit", 3), ("credit", 3), ("visa", 3),
        ]:
            if term in low:
                score += weight
        amount_count = len(re.findall(r"\b\d+[.,]\d{1,3}\b", text))
        score += min(amount_count, 40) * 1.2
        # Reward receipt structure and useful alphanumeric identifiers.
        if re.search(r"\b(?:tc|rcpt|receipt|txn|transaction|ref)\s*#?", low):
            score += 8
        if re.search(r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b", text):
            score += 8
        structured = sum(
            1 for line in lines
            if re.search(r"[A-Za-z].*\d+[.,]\d{1,3}\s*$", line["text"])
        )
        score += min(structured, 30) * 0.8
        # Penalize extremely long/noisy lines.
        noisy = sum(1 for line in lines if len(line["text"]) > 90)
        score -= noisy * 1.5
        # Penalize text that is mostly isolated punctuation/noise.
        words = re.findall(r"[A-Za-z]{2,}", text)
        if words:
            score += min(len(words), 60) * 0.05
        return score

    def _easyocr_pass(self, image: np.ndarray) -> List[Dict[str, Any]]:
        if not self._init_easyocr():
            return []
        try:
            rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            detections = self.easy_reader.readtext(rgb, detail=1, paragraph=False)
            return [
                {
                    "text": str(d[1]).strip(),
                    "confidence": round(float(d[2]) * 100, 2),
                    "engine": "easyocr",
                }
                for d in detections if len(d) >= 3 and str(d[1]).strip()
            ]
        except Exception as exc:
            print(f"EasyOCR warning: {exc}")
            return []

    def extract(self, image: Any) -> Dict[str, Any]:
        img = self._to_numpy(image)
        variants = self._variants(img)

        candidates: List[Tuple[float, str, List[Dict[str, Any]]]] = []
        if self.tesseract_available:
            for name, variant in variants:
                for psm in (6, 11):
                    lines = self._tesseract_pass(variant, psm)
                    lines = [
                        dict(x, text=self._clean(x["text"]))
                        for x in lines if self._clean(x["text"])
                    ]
                    if lines:
                        candidates.append((self._score(lines), f"tesseract:{name}:psm{psm}", lines))

        if candidates:
            candidates.sort(key=lambda x: x[0], reverse=True)
            score, engine, final_lines = candidates[0]
        else:
            final_lines = self._easyocr_pass(img)
            score = self._score(final_lines)
            engine = "easyocr"

        text = "\n".join(x["text"] for x in final_lines)
        confs = [float(x.get("confidence", 0)) for x in final_lines]
        confidence = sum(confs) / len(confs) if confs else 0.0

        return {
            "text": text,
            "ocr_text": text,
            "lines": final_lines,
            "confidence": round(confidence, 2),
            "line_count": len(final_lines),
            "engine": engine,
            "ocr_score": round(score, 2),
        }
