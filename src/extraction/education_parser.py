import re


class EducationParser:
    """Robust education parser for OCR text, including two-column CV layouts."""

    DEGREE_PATTERNS = [
        r"\bmatric(?:ulation)?\b",
        r"\bintermediate\b",
        r"\bf\.?sc\b",
        r"\bi\.?cs\b",
        r"\b(?:bachelor|bachlor)\b",
        r"\b(?:master|masters)\b",
        r"\b(?:b\.?\s*ed|bed)\b",
        r"\b(?:m\.?\s*ed|med)\b",
        r"\b(?:b\.?\s*sc|bsc)\b",
        r"\b(?:m\.?\s*sc|msc)\b",
        r"\b(?:b\.?\s*e|be)\b",
        r"\b(?:b\.?\s*tech|btech)\b",
        r"\b(?:m\.?\s*tech|mtech)\b",
        r"\b(?:mba|ph\.?\s*d|phd)\b",
    ]

    INSTITUTION_HINTS = (
        "university",
        "college",
        "institute",
        "school",
        "academy",
    )

    YEAR_RANGE_PATTERN = re.compile(
        r"\b(?:19|20)\d{2}\s*(?:-|–|—|to)\s*(?:19|20)\d{2}\b",
        re.IGNORECASE,
    )
    YEAR_PATTERN = re.compile(r"\b(?:19|20)\d{2}\b")

    IGNORE_EXACT = {
        "education",
        "academic background",
        "academic qualification",
        "qualifications",
        "qualification",
        "educational background",
        "city",
        "year",
    }

    def _is_degree(self, line: str) -> bool:
        lower = line.lower().strip()
        return any(re.search(pattern, lower) for pattern in self.DEGREE_PATTERNS)

    def _is_institution(self, line: str) -> bool:
        lower = line.lower().strip()
        return any(word in lower for word in self.INSTITUTION_HINTS)

    def _year(self, line: str):
        match = self.YEAR_RANGE_PATTERN.search(line)
        if match:
            return match.group(0)
        match = self.YEAR_PATTERN.search(line)
        return match.group(0) if match else None

    @staticmethod
    def _clean_degree(line: str) -> str:
        line = re.sub(r"\s+", " ", line).strip()
        # Common OCR typo seen in resumes.
        line = re.sub(r"\bBachlor\b", "Bachelor", line, flags=re.IGNORECASE)
        line = re.sub(r"\bMathamatics\b", "Mathematics", line, flags=re.IGNORECASE)
        return line

    @staticmethod
    def _looks_like_noise(line: str) -> bool:
        lower = line.lower().strip()
        noise = {
            "classroom management",
            "lesson planning",
            "student communication",
            "subject knowledge",
            "communication skills",
            "teaching",
            "tutoring",
            "online teaching",
            "physics",
            "mathematics",
            "english",
            "urdu",
            "pushto",
            "present",
            "goals.",
        }
        return lower in noise

    def parse(self, education_text):
        if isinstance(education_text, str):
            lines = [x.strip() for x in education_text.splitlines() if x.strip()]
        elif isinstance(education_text, list):
            lines = [str(x).strip() for x in education_text if str(x).strip()]
        else:
            return []

        # We intentionally scan the complete supplied text. OCR from two-column
        # resumes can interleave Education and Languages/Skills.
        records = []
        degree_indexes = [i for i, line in enumerate(lines) if self._is_degree(line)]

        for idx, degree_index in enumerate(degree_indexes):
            degree = self._clean_degree(lines[degree_index])
            next_degree = degree_indexes[idx + 1] if idx + 1 < len(degree_indexes) else len(lines)

            institution = None
            year = None

            # Search a small forward window, stopping at the next degree.
            for j in range(degree_index + 1, min(next_degree, degree_index + 10)):
                line = lines[j]

                if self._looks_like_noise(line):
                    continue

                found_year = self._year(line)
                if found_year and year is None:
                    year = found_year
                    continue

                if institution is None and self._is_institution(line):
                    institution = line
                    continue

            # If the institution was OCR'd before the degree, search a small
            # backward window. This is useful for layouts where columns reorder.
            if institution is None:
                for j in range(degree_index - 1, max(-1, degree_index - 6), -1):
                    line = lines[j]
                    if self._is_institution(line):
                        institution = line
                        break

            # Search a slightly wider local window for a year if needed.
            if year is None:
                for j in range(degree_index - 1, max(-1, degree_index - 6), -1):
                    found_year = self._year(lines[j])
                    if found_year:
                        year = found_year
                        break

            records.append({
                "degree": degree,
                "institution": institution,
                "year": year,
            })

        # Remove duplicates while preserving order.
        unique = []
        seen = set()
        for record in records:
            key = (
                record["degree"].lower() if record["degree"] else None,
                record["institution"].lower() if record["institution"] else None,
                record["year"],
            )
            if key not in seen:
                seen.add(key)
                unique.append(record)

        return unique
