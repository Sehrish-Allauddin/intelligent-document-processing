import json
import re
from pathlib import Path


class SkillMatcher:

    def __init__(self):

        skills_file = Path(
            "src/resources/skills.json"
        )

        with open(
            skills_file,
            "r",
            encoding="utf-8"
        ) as file:

            self.skills = json.load(file)

        if not isinstance(
            self.skills,
            list
        ):
            self.skills = []

    # --------------------------------------------------
    # NORMALIZE TEXT
    # --------------------------------------------------

    @staticmethod
    def normalize_text(text):

        if not text:
            return ""

        text = str(text).lower()

        # Normalize common separators
        text = text.replace(
            "&",
            " and "
        )

        text = re.sub(
            r"[-_/]+",
            " ",
            text
        )

        # Remove extra spaces
        text = re.sub(
            r"\s+",
            " ",
            text
        )

        return text.strip()

    # --------------------------------------------------
    # EXTRACT SKILLS
    # --------------------------------------------------

    def extract(self, text):

        if not text:
            return []

        normalized_text = self.normalize_text(
            text
        )

        found = set()

        for skill in self.skills:

            if not skill:
                continue

            skill_text = self.normalize_text(
                skill
            )

            if not skill_text:
                continue

            # ------------------------------------------
            # Exact phrase / word matching
            # ------------------------------------------

            pattern = (
                r"(?<!\w)"
                + re.escape(skill_text)
                + r"(?!\w)"
            )

            if re.search(
                pattern,
                normalized_text
            ):

                found.add(skill)

        return sorted(
            found,
            key=str.lower
        )

    # --------------------------------------------------
    # CONTAINS SKILL
    # --------------------------------------------------

    def contains(
        self,
        skill,
        text
    ):

        if not skill or not text:
            return False

        normalized_text = self.normalize_text(
            text
        )

        normalized_skill = self.normalize_text(
            skill
        )

        if not normalized_skill:
            return False

        pattern = (
            r"(?<!\w)"
            + re.escape(normalized_skill)
            + r"(?!\w)"
        )

        return (
            re.search(
                pattern,
                normalized_text
            )
            is not None
        )

    # --------------------------------------------------
    # COUNT
    # --------------------------------------------------

    def count(self, text):

        return len(
            self.extract(text)
        )