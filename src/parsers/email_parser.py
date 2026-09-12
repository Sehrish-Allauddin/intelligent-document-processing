import re


class EmailParser:

    @staticmethod
    def extract(text):

        match = re.search(
            r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
            text
        )

        if match:
            return match.group()

        return None