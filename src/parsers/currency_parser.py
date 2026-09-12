import re


class CurrencyParser:

    @staticmethod
    def extract(text):

        match = re.search(
            r"\b(PKR|USD|EUR|GBP|AED|SAR|INR|MYR)\b",
            text,
            re.IGNORECASE
        )

        if match:
            return match.group().upper()

        return None