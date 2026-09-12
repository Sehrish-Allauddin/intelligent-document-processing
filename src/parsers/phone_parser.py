import re


class PhoneParser:

    @staticmethod
    def extract(text):

        match = re.search(
            r"(\+?\d[\d\s\-]{8,}\d)",
            text
        )

        if match:
            return match.group()

        return None