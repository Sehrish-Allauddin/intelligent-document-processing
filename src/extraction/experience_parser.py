import re


class ExperienceParser:
    """Parse common resume experience layouts, including OCR'd year lines."""

    DATE_PATTERN = re.compile(
        r"\b((?:19|20)\d{2}\s*(?:-|–|—|to)\s*(?:(?:19|20)\d{2}|present))\b",
        re.IGNORECASE,
    )
    YEAR_PATTERN = re.compile(r"^(?:19|20)\d{2}$")

    IGNORE_LINES = {
        "experience",
        "professional experience",
        "work experience",
        "employment",
        "teaching experience",
        "professional background",
        "responsibilities",
        "responsibility",
        "duties",
        "job description",
    }

    CONTACT_HEADERS = {
        "contact",
        "contacts",
        "contact information",
        "contact details",
    }

    SECTION_HEADERS = {
        "education",
        "skills",
        "projects",
        "certifications",
        "languages",
        "summary",
        "profile",
        "about me",
    }

    BULLET_PREFIX = re.compile(r"^[•●▪◦\-–—*]+\s*")

    def parse(self, experience_text):
        if isinstance(experience_text, str):
            lines = [x.strip() for x in experience_text.splitlines() if x.strip()]
        elif isinstance(experience_text, list):
            lines = [str(x).strip() for x in experience_text if str(x).strip()]
        else:
            return []

        records = []
        current = None
        pending_years = []

        def new_record(title=None):
            return {
                "company": None,
                "job_title": title,
                "duration": None,
                "description": [],
            }

        def finalize():
            nonlocal current, pending_years
            if current is None:
                return
            if current.get("duration") is None and pending_years:
                if len(pending_years) >= 2:
                    current["duration"] = f"{pending_years[0]} - {pending_years[1]}"
                else:
                    current["duration"] = pending_years[0]
            pending_years = []
            # Remove accidental empty descriptions.
            current["description"] = [
                x for x in current.get("description", [])
                if x and x.strip()
            ]
            if (
                current.get("job_title")
                or current.get("company")
                or current.get("duration")
                or current.get("description")
            ):
                records.append(current)
            current = None

        for raw_line in lines:
            line = raw_line.strip()
            lower = line.lower()

            if lower in self.CONTACT_HEADERS:
                # OCR from two-column resumes may place the CONTACTS label
                # between two parts of the experience column. Do not terminate
                # the record; simply ignore the label.
                continue

            if "@" in line or re.search(r"\+?\d[\d\s()\-]{8,}", line):
                continue

            if lower in self.SECTION_HEADERS:
                # The caller normally supplies only the experience section, but
                # stopping here prevents OCR spillover from corrupting records.
                if lower != "about me":
                    finalize()
                    break

            if lower in self.IGNORE_LINES:
                continue

            date_match = self.DATE_PATTERN.search(line)
            if date_match:
                if current is None:
                    current = new_record()
                current["duration"] = date_match.group(1)
                continue

            if self.YEAR_PATTERN.fullmatch(line):
                if current is None:
                    current = new_record()
                pending_years.append(line)
                continue

            company_match = re.match(
                r"^(?:company|organization|employer)\s*:\s*(.+)$",
                line,
                re.IGNORECASE,
            )
            if company_match:
                if current is None:
                    current = new_record()
                current["company"] = company_match.group(1).strip()
                continue

            # First meaningful line is the job title.
            if current is None:
                current = new_record(line)
                continue

            # A short subtitle immediately after a short title is often a role
            # specialization. Merge it only before any dates/descriptions.
            if (
                not current["description"]
                and current["duration"] is None
                and not pending_years
                and current["job_title"]
                and len(current["job_title"].split()) <= 4
                and len(line.split()) <= 10
            ):
                current["job_title"] = f"{current['job_title']} - {line}"
                continue

            cleaned = self.BULLET_PREFIX.sub("", line).strip()

            # OCR column spill: institution/contact lists can appear inside
            # the experience section. They are not a job description.
            if (
                re.search(r"\b(?:school|academy|college|university)\b", cleaned, re.IGNORECASE)
                and re.search(r",\s*(?:Peshawar|Swabi|Islamabad|Lahore|Karachi)\b", cleaned, re.IGNORECASE)
            ):
                continue

            if cleaned:
                # Join OCR-wrapped continuation lines with the previous bullet.
                if (
                    current["description"]
                    and cleaned[0].islower()
                    and not self.BULLET_PREFIX.match(line)
                ):
                    current["description"][-1] = (
                        current["description"][-1].rstrip() + " " + cleaned
                    )
                else:
                    current["description"].append(cleaned)

        finalize()
        return records
