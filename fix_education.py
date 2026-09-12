from pathlib import Path
import re

path = Path(r".\src\extraction\resume_extractor.py")
text = path.read_text(encoding="utf-8")

start = text.index("    def _fallback_education(self, text):")
end = text.index("    def _fallback_experience(self, text):", start)

new_method = r'''    def _fallback_education(self, text):
        """
        Generic education extractor.

        Works with different CV layouts without relying on specific
        candidate names, universities, degrees, or institutions.
        """

        if not text:
            return []

        import re

        def clean(value):
            return re.sub(r"\s+", " ", str(value or "")).strip()

        def normalize(value):
            value = clean(value).lower()
            value = re.sub(r"[^a-z0-9&+./#' -]", " ", value)
            return re.sub(r"\s+", " ", value).strip()

        lines = [
            clean(line)
            for line in str(text).splitlines()
            if clean(line)
        ]

        if not lines:
            return []

        education_headers = {
            "education",
            "educational background",
            "education background",
            "academic background",
            "academic qualifications",
            "academic history",
            "qualifications",
            "educational qualifications",
            "education & qualifications",
            "education and qualifications",
        }

        stop_headers = {
            "experience",
            "work experience",
            "professional experience",
            "employment",
            "employment history",
            "career history",
            "work history",
            "skills",
            "technical skills",
            "professional skills",
            "core skills",
            "key skills",
            "competencies",
            "expertise",
            "projects",
            "personal projects",
            "certifications",
            "certificates",
            "languages",
            "references",
            "achievements",
            "awards",
            "interests",
            "hobbies",
            "contact",
            "contacts",
            "personal details",
            "summary",
            "profile",
            "objective",
            "career objective",
            "about me",
        }

        # Broad qualification signals.
        # These are generic category words, not specific institutions.
        degree_pattern = re.compile(
            r"\b("
            r"ph\.?d|doctorate|doctoral|"
            r"master(?:'s)?|m\.?sc|m\.?a|m\.?s|mba|m\.?phil|"
            r"bachelor(?:'s)?|b\.?sc|b\.?a|b\.?s|bba|b\.?com|"
            r"associate|diploma|"
            r"higher secondary|secondary school|high school|"
            r"intermediate|matric|"
            r"foundation|certificate|certification|"
            r"llb|jd|md|mbbs|bds|pharmd|"
            r"engineering|computer science|information technology|"
            r"data science|business administration|"
            r"accounting|finance|economics|"
            r"education|arts|commerce|science"
            r")\b",
            re.I,
        )

        date_pattern = re.compile(
            r"\b(?:"
            r"(?:19|20)\d{2}\s*(?:-|–|—|to)\s*"
            r"(?:(?:19|20)\d{2}|present|current|ongoing)"
            r"|"
            r"(?:19|20)\d{2}"
            r")\b",
            re.I,
        )

        month_year_pattern = re.compile(
            r"\b(?:"
            r"jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|"
            r"may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|"
            r"sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?"
            r")\s+(?:19|20)\d{2}\b",
            re.I,
        )

        def is_date(line):
            return bool(
                date_pattern.search(line)
                or month_year_pattern.search(line)
            )

        def extract_date(line):
            match = date_pattern.search(line)
            if match:
                return clean(match.group(0))

            match = month_year_pattern.search(line)
            if match:
                return clean(match.group(0))

            return None

        # --------------------------------------------------
        # FIND EDUCATION AREA
        # --------------------------------------------------

        start = None

        for i, line in enumerate(lines):
            if normalize(line) in education_headers:
                start = i + 1
                break

        if start is not None:
            end = len(lines)

            for i in range(start, len(lines)):
                if normalize(lines[i]) in stop_headers:
                    end = i
                    break

            area = lines[start:end]

        else:
            # No heading: locate qualification evidence.
            positions = [
                i for i, line in enumerate(lines)
                if degree_pattern.search(line)
            ]

            if not positions:
                return []

            start = max(0, positions[0] - 2)

            # Continue until another strong section header.
            end = len(lines)

            for i in range(positions[-1] + 1, len(lines)):
                if normalize(lines[i]) in stop_headers:
                    end = i
                    break

            area = lines[start:end]

        if not area:
            return []

        # --------------------------------------------------
        # IDENTIFY EDUCATION RECORD ANCHORS
        # --------------------------------------------------

        degree_positions = [
            i for i, line in enumerate(area)
            if degree_pattern.search(line)
        ]

        if not degree_positions:
            return []

        records = []

        for pos_number, degree_index in enumerate(degree_positions):

            # Each qualification owns the text up to the next
            # qualification. This prevents one qualification's
            # date from leaking into another.
            next_degree = (
                degree_positions[pos_number + 1]
                if pos_number + 1 < len(degree_positions)
                else len(area)
            )

            block_start = degree_index
            block_end = next_degree

            block = area[block_start:block_end]

            if not block:
                continue

            degree = clean(area[degree_index])

            if not degree:
                continue

            # --------------------------------------------------
            # DATE
            # --------------------------------------------------

            year = None

            # First prefer dates after the degree.
            for line in block[1:]:
                candidate = extract_date(line)

                if candidate:
                    year = candidate
                    break

            # If no date follows it, allow a date immediately
            # before the degree.
            if year is None and degree_index > 0:
                previous = area[degree_index - 1]
                candidate = extract_date(previous)

                if candidate:
                    year = candidate

            # --------------------------------------------------
            # INSTITUTION
            # --------------------------------------------------

            institution = None
            institution_candidates = []

            institution_keywords = re.compile(
                r"\b("
                r"school|college|university|academy|"
                r"institute|faculty|campus|"
                r"polytechnic|department|"
                r"board|institute|centre|center"
                r")\b",
                re.I,
            )

            for relative_index, line in enumerate(block[1:], start=1):

                candidate = clean(line)

                if not candidate:
                    continue

                if is_date(candidate):
                    continue

                if normalize(candidate) in stop_headers:
                    continue

                # Do not select another qualification as institution.
                if degree_pattern.search(candidate):
                    continue

                # Long prose is more likely a description.
                if len(candidate.split()) > 10:
                    continue

                # Common academic-status sentences are not institutions.
                if re.match(
                    r"^(completed|graduated|studied|pursuing|"
                    r"currently|major|specialization|"
                    r"specialised|specialized|"
                    r"coursework|thesis|cgpa|gpa)\b",
                    candidate,
                    re.I,
                ):
                    continue

                score = 0

                if institution_keywords.search(candidate):
                    score += 5

                # Institution generally appears close to the degree.
                score += max(0, 4 - relative_index)

                # Short standalone names are plausible institution names.
                if 1 <= len(candidate.split()) <= 7:
                    score += 1

                institution_candidates.append(
                    (score, relative_index, candidate)
                )

            if institution_candidates:
                institution_candidates.sort(
                    key=lambda item: (-item[0], item[1])
                )
                institution = institution_candidates[0][2]

            # --------------------------------------------------
            # FALLBACK INSTITUTION
            # --------------------------------------------------

            # If no keyword-based institution was found, use a short
            # non-date, non-degree line immediately following the degree.
            if institution is None:

                for candidate in block[1:4]:

                    candidate = clean(candidate)

                    if not candidate:
                        continue

                    if is_date(candidate):
                        continue

                    if degree_pattern.search(candidate):
                        continue

                    if normalize(candidate) in stop_headers:
                        continue

                    if len(candidate.split()) <= 7:
                        institution = candidate
                        break

            # --------------------------------------------------
            # VALIDATION
            # --------------------------------------------------

            normalized_degree = normalize(degree)

            if normalized_degree in stop_headers:
                continue

            # Reject obvious section labels.
            if len(normalized_degree.split()) <= 1 and normalized_degree in {
                "education",
                "experience",
                "skills",
                "projects",
                "languages",
            }:
                continue

            records.append(
                {
                    "degree": degree,
                    "institution": institution,
                    "year": year,
                }
            )

        # --------------------------------------------------
        # DEDUPLICATION
        # --------------------------------------------------

        cleaned_records = []
        seen = set()

        for record in records:

            key = (
                normalize(record.get("degree")),
                normalize(record.get("institution")),
                normalize(record.get("year")),
            )

            if key in seen:
                continue

            seen.add(key)
            cleaned_records.append(record)

        return cleaned_records

'''

path.write_text(text[:start] + new_method + text[end:], encoding="utf-8")

print("EDUCATION METHOD REPLACED")
print(path.resolve())