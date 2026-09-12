import re


class OCRCorrector:
    """
    Production OCR Error Correction Engine

    Corrects common OCR mistakes without
    damaging numbers like invoice totals,
    dates, phone numbers or IDs.
    """

    REPLACEMENTS = {

        # -------------------------
        # Programming Skills
        # -------------------------

        "Pyth0n": "Python",
        "Pythn": "Python",
        "Phyton": "Python",

        "Tensor Fl0w": "TensorFlow",
        "Tensorflow": "TensorFlow",

        "Panda5": "Pandas",
        "Pandass": "Pandas",

        "NumpY": "NumPy",
        "Num Py": "NumPy",

        "Open CV": "OpenCV",

        "Scikit Learn": "Scikit-Learn",

        # -------------------------
        # Developer Tools
        # -------------------------

        "Git Hub": "GitHub",

        "Linkedln": "LinkedIn",

        "Micr0soft": "Microsoft",

        "GmaiI": "Gmail",

        "Amaz0n": "Amazon",

        # -------------------------
        # AI Frameworks
        # -------------------------

        "Pyt0rch": "PyTorch",

        "Tensor FIow": "TensorFlow",

        "Kera5": "Keras",

        # -------------------------
        # Misc
        # -------------------------

        "E-maiI": "Email",

        "MaiI": "Mail"

    }

    @classmethod
    def correct(cls, text):

        if not text:

            return ""

        corrected = text

        # -------------------------
        # Dictionary Corrections
        # -------------------------

        for wrong, right in cls.REPLACEMENTS.items():

            corrected = re.sub(

                re.escape(wrong),

                right,

                corrected,

                flags=re.IGNORECASE

            )

        # -------------------------
        # Remove Multiple Spaces
        # -------------------------

        corrected = re.sub(

            r"[ ]{2,}",

            " ",

            corrected

        )

        # -------------------------
        # Remove Extra Blank Lines
        # -------------------------

        corrected = re.sub(

            r"\n{3,}",

            "\n\n",

            corrected

        )

        return corrected.strip()