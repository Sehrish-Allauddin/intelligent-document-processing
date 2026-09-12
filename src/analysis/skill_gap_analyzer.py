class SkillGapAnalyzer:

    def analyze(self, jd_result):

        missing_skills = jd_result.get(
            "missing_skills",
            []
        )

        learning_priority = []

        for skill in missing_skills:

            learning_priority.append({

                "skill": skill,

                "priority": "High"

            })

        if missing_skills:

            recommendation = (

                "Learning "

                + ", ".join(missing_skills)

                + " can significantly improve "

                  "your chances for this role."

            )

        else:

            recommendation = (

                "Excellent! Your resume covers "

                "all required skills."

            )

        return {

            "learning_priority": learning_priority,

            "career_recommendation": recommendation

        }