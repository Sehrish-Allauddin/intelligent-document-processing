import re


class ResumeSectionSplitter:

    SECTION_HEADERS = {
        "summary": [
            "professional summary",
            "summary",
            "profile",
            "objective"
        ],
        "skills": [
            "skills",
            "technical skills",
            "core skills"
        ],
        "experience": [
            "experience",
            "professional experience",
            "work experience",
            "employment"
        ],
        "projects": [
            "projects",
            "project"
        ],
        "education": [
            "education",
            "academic background",
            "qualification"
        ],
        "certifications": [
            "certifications",
            "certificates",
            "licenses"
        ],
        "languages": [
            "languages"
        ]
    }

    def split(self, text):

        sections = {key: "" for key in self.SECTION_HEADERS}

        sections["profile"] = ""

        current = "profile"

        for line in text.split("\n"):

            line = line.strip()

            if not line:
                continue

            lower = line.lower()

            found = False

            for section, headers in self.SECTION_HEADERS.items():

                for header in headers:

                    if header in lower:

                        current = section
                        found = True
                        break

                if found:
                    break

            if not found:

                sections[current] += line + "\n"

        return sections