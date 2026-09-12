from src.ats.scoring_rules import SCORING_RULES


class ATSScorer:

    def score(self, resume):

        score = 0

        recommendations = []

        breakdown = {}

        # -------------------------
        # Name
        # -------------------------

        if resume.get("name"):

            score += SCORING_RULES["name"]

            breakdown["name"] = SCORING_RULES["name"]

        else:

            breakdown["name"] = 0

            recommendations.append(
                "Add your full name."
            )

        # -------------------------
        # Email
        # -------------------------

        if resume.get("email"):

            score += SCORING_RULES["email"]

            breakdown["email"] = SCORING_RULES["email"]

        else:

            breakdown["email"] = 0

            recommendations.append(
                "Add a professional email address."
            )

        # -------------------------
        # Phone
        # -------------------------

        if resume.get("phone"):

            score += SCORING_RULES["phone"]

            breakdown["phone"] = SCORING_RULES["phone"]

        else:

            breakdown["phone"] = 0

            recommendations.append(
                "Add your phone number."
            )

        # -------------------------
        # Skills
        # -------------------------

        skills = resume.get("skills", [])

        if len(skills) >= 10:

            score += SCORING_RULES["skills"]

            breakdown["skills"] = SCORING_RULES["skills"]

        elif len(skills) >= 5:

            score += 15

            breakdown["skills"] = 15

            recommendations.append(
                "Add more relevant technical skills."
            )

        else:

            breakdown["skills"] = 0

            recommendations.append(
                "Increase technical skills."
            )

        # -------------------------
        # Education
        # -------------------------

        education = resume.get("education", [])

        if education:

            score += SCORING_RULES["education"]

            breakdown["education"] = SCORING_RULES["education"]

        else:

            breakdown["education"] = 0

            recommendations.append(
                "Add education details."
            )

        # -------------------------
        # Experience
        # -------------------------

        experience = resume.get("experience", [])

        if experience:

            score += SCORING_RULES["experience"]

            breakdown["experience"] = SCORING_RULES["experience"]

        else:

            breakdown["experience"] = 0

            recommendations.append(
                "Add work experience."
            )

        # -------------------------
        # Projects
        # -------------------------

        projects = resume.get("projects", [])

        if projects:

            score += SCORING_RULES["projects"]

            breakdown["projects"] = SCORING_RULES["projects"]

        else:

            breakdown["projects"] = 0

            recommendations.append(
                "Add portfolio projects."
            )

        # -------------------------
        # Certifications
        # -------------------------

        certifications = resume.get(
            "certifications",
            []
        )

        if certifications:

            score += SCORING_RULES["certifications"]

            breakdown["certifications"] = 5

        else:

            breakdown["certifications"] = 0

        # -------------------------
        # LinkedIn
        # -------------------------

        if resume.get("linkedin"):

            score += SCORING_RULES["linkedin"]

            breakdown["linkedin"] = 5

        else:

            breakdown["linkedin"] = 0

            recommendations.append(
                "Add LinkedIn profile."
            )

        # -------------------------
        # GitHub
        # -------------------------

        if resume.get("github"):

            score += SCORING_RULES["github"]

            breakdown["github"] = 5

        else:

            breakdown["github"] = 0

            recommendations.append(
                "Add GitHub profile."
            )

        # -------------------------
        # FINAL SCORE LIMIT
        # -------------------------

        score = min(100, max(0, score))

        return {

            "overall_score": score,

            "breakdown": breakdown,

            "recommendations": recommendations

        }