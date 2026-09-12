from src.analysis.skill_gap_analyzer import SkillGapAnalyzer

jd_result = {

    "match_score": 60,

    "matched_skills": [

        "Python",

        "SQL",

        "Machine Learning"

    ],

    "missing_skills": [

        "AWS",

        "Docker"

    ]

}

analyzer = SkillGapAnalyzer()

result = analyzer.analyze(jd_result)

print(result)