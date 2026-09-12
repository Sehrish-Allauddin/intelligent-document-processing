import re


class EducationExtractor:
    """
    Lightweight education extractor used by ResumeExtractor.
    Designed to work even when OCR text has poor formatting.
    """

    def __init__(self):
        pass

    def extract(self, text):
        if not text:
            return []

        lines = [
            line.strip()
            for line in text.splitlines()
            if line.strip()
        ]

        results = []

        degree_patterns = [
            r"\bmatric(?:ulation)?\b",
            r"\bintermediate\b",
            r"\b(?:fsc|fa|ics|icom)\b",
            r"\bbachelor\b",
            r"\bb\.?s\.?\b",
            r"\bbs\b",
            r"\bb\.?sc\b",
            r"\bmaster\b",
            r"\bm\.?s\.?\b",
            r"\bmsc\b",
            r"\bm\.?phil\b",
            r"\bphd\b",
            r"\bdoctorate\b",
            r"\bb\.?ed\b",
            r"\bm\.?ed\b",
            r"\bdiploma\b",
        ]

        degree_regex = re.compile(
            "|".join(degree_patterns),
            re.IGNORECASE
        )

        year_regex = re.compile(
            r"\b(?:19|20)\d{2}\b"
            r"(?:\s*(?:to|-|–|—)\s*(?:19|20)\d{2})?"
            r"(?:\s*(?:expected|present|current))?",
            re.IGNORECASE
        )

        section_words = {
            "education",
            "academic background",
            "academic qualification",
            "qualifications",
            "qualification",
            "educational background",
        }

        stop_sections = {
            "experience",
            "work experience",
            "employment",
            "projects",
            "certifications",
            "certificates",
            "skills",
            "languages",
            "contact",
            "contacts",
            "references",
        }

        # Find education section if available
        start = None
        end = len(lines)

        for i, line in enumerate(lines):
            low = line.lower().strip(" :.-")

            if low in section_words:
                start = i + 1
                break

        if start is not None:
            for i in range(start, len(lines)):
                low = lines[i].lower().strip(" :.-")
                if low in stop_sections:
                    end = i
                    break

            education_lines = lines[start:end]
        else:
            education_lines = lines

        # Find degree records
        for i, line in enumerate(education_lines):
            if not degree_regex.search(line):
                continue

            degree = line.strip()

            # Clean obvious OCR noise
            degree = re.sub(r"\s+", " ", degree)

            institution = None
            year = None

            # Search nearby lines for institution/year
            nearby = education_lines[i + 1:i + 4]

            for candidate in nearby:
                if not year:
                    year_match = year_regex.search(candidate)
                    if year_match:
                        year = year_match.group(0).strip()

                if not institution:
                    candidate_low = candidate.lower()

                    if (
                        not degree_regex.search(candidate)
                        and not year_regex.search(candidate)
                        and len(candidate.split()) >= 2
                        and candidate_low not in section_words
                        and candidate_low not in stop_sections
                    ):
                        institution = candidate.strip()

            # Year may be on same line
            if not year:
                year_match = year_regex.search(degree)
                if year_match:
                    year = year_match.group(0).strip()

            # Remove year from degree
            if year:
                degree = re.sub(
                    re.escape(year),
                    "",
                    degree,
                    flags=re.IGNORECASE
                ).strip(" -,:;")

            results.append({
                "degree": degree or None,
                "institution": institution,
                "year": year,
            })

        return self._deduplicate(results)

    def _deduplicate(self, records):
        output = []
        seen = set()

        for record in records:
            key = (
                str(record.get("degree") or "").lower().strip(),
                str(record.get("institution") or "").lower().strip(),
                str(record.get("year") or "").lower().strip(),
            )

            if key in seen:
                continue

            seen.add(key)
            output.append(record)

        return output

    def extract_education(self, text):
        """
        Compatibility method for older ResumeExtractor versions.
        """
        return self.extract(text)