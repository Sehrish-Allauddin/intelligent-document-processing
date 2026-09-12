class SectionDetector:

    SECTION_HEADERS = {

        "summary": [
            "summary",
            "professional summary",
            "profile",
            "objective",
            "career summary",
            "career objective",
            "about me"
        ],

        "skills": [
            "skills",
            "technical skills",
            "technical skill",
            "core skills",
            "key skills",
            "technical expertise",
            "competencies",
            "additional information"
        ],

        "experience": [
            "experience",
            "work experience",
            "professional experience",
            "employment",
            "employment history",
            "career history"
        ],

        "education": [
            "education",
            "academic background",
            "qualification",
            "qualifications",
            "academic qualifications"
        ],

        "projects": [
            "projects",
            "project",
            "academic projects",
            "personal projects",
            "project work"
        ],

        "certifications": [
            "certifications",
            "certification",
            "licenses",
            "training"
        ],

        "languages": [
            "languages",
            "language"
        ],

        "achievements": [
            "achievements",
            "awards",
            "honors",
            "accomplishments",
            "highlights"
        ]
    }

    def detect(self, lines):

        sections = {
            key: []
            for key in self.SECTION_HEADERS
        }

        current = None

        for line in lines:

            text = line.strip()

            if not text:
                continue

            lower = text.lower()

            matched = False

            for section, headers in self.SECTION_HEADERS.items():

                for header in headers:

                    if header in lower:

                        current = section
                        matched = True
                        break

                if matched:
                    break

            if matched:
                continue

            if current:
                sections[current].append(text)

        return sections