class ResumeParser:
    """Split OCR text into logical resume sections."""

    SECTION_HEADERS = {
        "summary": [
            "professional summary", "summary", "profile", "objective",
            "about me", "career objective", "professional profile",
            "personal profile",
        ],
        "contact": [
            "contact", "contacts", "contact information", "contact details",
            "personal details",
        ],
        "skills": [
            "skills", "technical skills", "core skills", "key skills",
            "professional skills", "competencies",
        ],
        "experience": [
            "experience", "professional experience", "work experience",
            "employment", "employment history", "work history",
            "teaching experience", "professional background", "career history",
        ],
        "projects": [
            "projects", "project", "academic projects", "personal projects",
            "portfolio projects", "key projects",
        ],
        "education": [
            "education", "academic background", "academic qualification",
            "qualifications", "qualification", "educational background",
        ],
        "certifications": [
            "certifications", "certificates", "licenses", "licences",
            "professional certifications",
        ],
        "languages": [
            "languages", "language", "language skills",
        ],
    }

    def __init__(self):
        pass

    @staticmethod
    def clean_header(text):
        if not isinstance(text, str):
            return ""
        text = text.lower().strip()
        text = text.replace(":", "").replace("-", " ").replace("_", " ")
        return " ".join(text.split())

    def find_section(self, line):
        cleaned = self.clean_header(line)
        if not cleaned:
            return None
        for section, headers in self.SECTION_HEADERS.items():
            for header in headers:
                if cleaned == self.clean_header(header):
                    return section
        return None

    def parse(self, text):
        sections = {
            "profile": [],
            "summary": [],
            "contact": [],
            "skills": [],
            "experience": [],
            "projects": [],
            "education": [],
            "certifications": [],
            "languages": [],
        }
        if not text:
            return sections
        if not isinstance(text, str):
            text = str(text)

        lines = [x.strip() for x in text.splitlines() if x and x.strip()]
        current = "profile"

        for line in lines:
            found = self.find_section(line)
            if found:
                current = found
                continue
            if current not in sections:
                current = "profile"
            sections[current].append(line)

        return sections
