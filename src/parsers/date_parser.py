import re


class DateParser:

    @staticmethod
    def extract(text):

        match = re.search(
            r"\d{1,2}[/-]\d{1,2}[/-]\d{2,4}",
            text
        )

        if not match:
            return None

        return (
            match.group()
            .replace("O", "0")
            .replace("o", "0")
        )