import re

from src.extraction.skill_matcher import SkillMatcher


class JDMatcher:

    def __init__(self):

        self.skill_matcher = SkillMatcher()

    def match(self, resume, job_description):

        resume_skills = set(

            resume.get("skills", [])

        )

        jd_skills = set(

            self.skill_matcher.extract(

                job_description

            )

        )

        matched = sorted(

            resume_skills.intersection(

                jd_skills

            )

        )

        missing = sorted(

            jd_skills - resume_skills

        )

        if len(jd_skills) == 0:

            score = 0

        else:

            score = round(

                len(matched)

                / len(jd_skills)

                * 100,

                2

            )

        recommendations = []

        if missing:

            recommendations.append(

                "Learn these skills: "

                + ", ".join(missing)

            )

        else:

            recommendations.append(

                "Excellent match for this job."

            )

        return {

            "match_score": score,

            "matched_skills": matched,

            "missing_skills": missing,

            "recommendations": recommendations

        }