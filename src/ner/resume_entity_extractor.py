import re


class ResumeEntityExtractor:

    EMAIL_PATTERN = (
        r"[A-Za-z0-9._%+-]+"
        r"@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"
    )

    PHONE_PATTERN = (
        r"(?:\+?\d{1,3}[\s-]?)?"
        r"(?:\(?\d{2,5}\)?[\s-]?)?"
        r"\d{3,5}[\s-]?\d{3,5}"
    )

    LINKEDIN_PATTERN = (
        r"(?:https?://)?"
        r"(?:www\.)?"
        r"linkedin\.com/in/[^\s]+"
    )

    GITHUB_PATTERN = (
        r"(?:https?://)?"
        r"(?:www\.)?"
        r"github\.com/[^\s]+"
    )

    WEBSITE_PATTERN = (
        r"(?:https?://)?"
        r"(?:www\.)?"
        r"[A-Za-z0-9-]+\.[A-Za-z]{2,}"
    )

    def extract(self, text):

        # --------------------------------------------------
        # ALWAYS RETURN DICTIONARY
        # --------------------------------------------------

        data = {
            "name": None,
            "email": None,
            "phone": None,
            "linkedin": None,
            "github": None,
            "website": None
        }

        # --------------------------------------------------
        # Safety
        # --------------------------------------------------

        if text is None:
            return data

        if not isinstance(text, str):
            text = str(text)

        if not text.strip():
            return data

        # --------------------------------------------------
        # Clean text
        # --------------------------------------------------

        text = text.strip()

        # --------------------------------------------------
        # EMAIL
        # --------------------------------------------------

        try:

            email = re.search(
                self.EMAIL_PATTERN,
                text,
                re.IGNORECASE
            )

            if email:
                data["email"] = email.group(0).strip()

        except Exception as e:

            print(
                "Email extraction error:",
                e
            )

        # --------------------------------------------------
        # PHONE
        # --------------------------------------------------

        try:

            phone = re.search(
                self.PHONE_PATTERN,
                text
            )

            if phone:

                phone_value = phone.group(0).strip()

                # Avoid very short invalid matches
                digits = re.sub(
                    r"\D",
                    "",
                    phone_value
                )

                if len(digits) >= 8:

                    data["phone"] = phone_value

        except Exception as e:

            print(
                "Phone extraction error:",
                e
            )

        # --------------------------------------------------
        # LINKEDIN
        # --------------------------------------------------

        try:

            linkedin = re.search(
                self.LINKEDIN_PATTERN,
                text,
                re.IGNORECASE
            )

            if linkedin:

                data["linkedin"] = linkedin.group(0).strip()

        except Exception as e:

            print(
                "LinkedIn extraction error:",
                e
            )

        # --------------------------------------------------
        # GITHUB
        # --------------------------------------------------

        try:

            github = re.search(
                self.GITHUB_PATTERN,
                text,
                re.IGNORECASE
            )

            if github:

                data["github"] = github.group(0).strip()

        except Exception as e:

            print(
                "GitHub extraction error:",
                e
            )

        # --------------------------------------------------
        # WEBSITE
        # --------------------------------------------------

        try:

            websites = re.findall(
                self.WEBSITE_PATTERN,
                text,
                re.IGNORECASE
            )

            for website in websites:

                website_lower = website.lower()

                # Do NOT treat email domain as website
                if "@" in website:
                    continue

                # Ignore LinkedIn
                if "linkedin.com" in website_lower:
                    continue

                # Ignore GitHub
                if "github.com" in website_lower:
                    continue

                # Ignore Gmail
                if "gmail.com" in website_lower:
                    continue

                data["website"] = website.strip()

                break

        except Exception as e:

            print(
                "Website extraction error:",
                e
            )

        # --------------------------------------------------
        # NAME
        # --------------------------------------------------

        try:

            lines = [
                line.strip()
                for line in text.split("\n")
                if line.strip()
            ]

            # First few OCR lines usually contain name
            for line in lines[:8]:

                clean_line = line.strip()

                lower = clean_line.lower()

                # Ignore common labels
                ignored = [
                    "phone",
                    "email",
                    "address",
                    "linkedin",
                    "github",
                    "website",
                    "professional summary",
                    "summary",
                    "data scientist",
                    "data analyst",
                    "resume",
                    "curriculum vitae",
                    "cv"
                ]

                if lower in ignored:
                    continue

                # Ignore contact information
                if "@" in clean_line:
                    continue

                if "linkedin.com" in lower:
                    continue

                if "github.com" in lower:
                    continue

                # Ignore phone-like text
                if re.search(
                    r"\d{5,}",
                    clean_line
                ):
                    continue

                words = clean_line.split()

                # Name should normally have 2-5 words
                if not (
                    2 <= len(words) <= 5
                ):
                    continue

                # Only alphabetic name-like words
                valid = True

                for word in words:

                    word_clean = re.sub(
                        r"[^A-Za-zÀ-ÿ'-]",
                        "",
                        word
                    )

                    if not word_clean:
                        valid = False
                        break

                if not valid:
                    continue

                # Avoid section headings
                if clean_line.upper() == clean_line:
                    continue

                data["name"] = clean_line
                break

        except Exception as e:

            print(
                "Name extraction error:",
                e
            )

        # --------------------------------------------------
        # FINAL SAFETY
        # --------------------------------------------------

        if not isinstance(data, dict):
            data = {
                "name": None,
                "email": None,
                "phone": None,
                "linkedin": None,
                "github": None,
                "website": None
            }

        print(
            "\nREGEX ENTITY RESULT:",
            data
        )

        return data