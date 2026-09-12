import re


class ResumeNormalizer:

    REPLACEMENTS = {

        "Pyth0n": "Python",
        "Machlne": "Machine",
        "Learnlng": "Learning",
        "TensorfIow": "TensorFlow",
        "Git Hub": "GitHub",
        "Linked In": "LinkedIn",
        "SqL": "SQL",
        "Javascrlpt": "JavaScript",
        "C Plus Plus": "C++",
        "AWSs": "AWS",

    }

    def normalize(self, text):

        if not text:
            return text

        # ---------------------------------
        # OCR Word Corrections
        # ---------------------------------

        for wrong, correct in self.REPLACEMENTS.items():

            text = text.replace(
                wrong,
                correct
            )

        # ---------------------------------
        # Remove extra spaces
        # (Preserve new lines)
        # ---------------------------------

        text = re.sub(
            r"[ \t]+",
            " ",
            text
        )

        # ---------------------------------
        # Remove extra blank lines
        # ---------------------------------

        text = re.sub(
            r"\n{2,}",
            "\n",
            text
        )

        # ---------------------------------
        # Remove spaces around new lines
        # ---------------------------------

        text = re.sub(
            r" *\n *",
            "\n",
            text
        )

        return text.strip()