import re


class WebsiteParser:

    @staticmethod
    def extract(text):

        match = re.search(
            r"https?://[^\s]+",
            text
        )

        if match:
            return match.group()

        return None