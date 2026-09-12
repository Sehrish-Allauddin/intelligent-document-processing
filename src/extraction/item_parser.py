import re


class ItemParser:

    def parse(self, lines):

        items = []

        for i, line in enumerate(lines):

            text = line.strip()

            if not text:
                continue

            upper = text.upper()

            # Ignore totals and headings
            ignore = [

                "TOTAL",
                "GST",
                "VAT",
                "AMOUNT",
                "DESCRIPTION",
                "PRICE",
                "QTY",
                "SUBTOTAL",
                "ROUND",
                "APPROVAL",
                "CARD",
                "THANK",
                "GOODS SOLD"

            ]

            if any(word in upper for word in ignore):
                continue

            # Product line
            if len(text) > 8 and any(c.isalpha() for c in text):

                quantity = None
                unit_price = None
                amount = None

                # Next lines may contain Qty
                if i + 1 < len(lines):

                    qty_match = re.search(

                        r"Qty[: ]*(\d+)",

                        lines[i + 1],

                        re.IGNORECASE

                    )

                    if qty_match:

                        quantity = int(qty_match.group(1))

                # Previous line may contain price
                if i >= 2:

                    numbers = re.findall(

                        r"\d+[.,]\d{2}",

                        lines[i - 2]

                    )

                    if numbers:

                        unit_price = float(

                            numbers[-1].replace(",", ".")

                        )

                        amount = unit_price

                if quantity or unit_price:

                    items.append({

                        "description": text,

                        "quantity": quantity,

                        "unit_price": unit_price,

                        "amount": amount

                    })

        return items