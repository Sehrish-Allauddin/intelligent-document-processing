from src.matching.jd_matcher import JDMatcher
from src.ats.ats_scorer import ATSScorer
from src.matching.jd_matcher import JDMatcher
from src.analysis.skill_gap_analyzer import SkillGapAnalyzer


class ResumeAIService:

    def __init__(self):

        self.ats = ATSScorer()

        self.matcher = JDMatcher()

        self.skill_gap = SkillGapAnalyzer()

    def analyze(self, resume, job_description=None):

        result = {}

        # ----------------------------
        # ATS Score
        # ----------------------------

        result["ats"] = self.ats.score(resume)

        # ----------------------------
        # JD Match (Optional)
        # ----------------------------

        if job_description:

            jd_result = self.matcher.match(

                resume,

                job_description

            )

            gap_result = self.skill_gap.analyze(

                jd_result

            )

            result["jd_match"] = jd_result

            result["skill_gap"] = gap_result

        return result