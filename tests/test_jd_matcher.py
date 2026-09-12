from src.matching.jd_matcher import JDMatcher

resume = {

    "skills": [

        "Python",

        "SQL",

        "TensorFlow",

        "Machine Learning"

    ]

}

job_description = """

Looking for

Python

SQL

Docker

AWS

Machine Learning

"""

matcher = JDMatcher()

result = matcher.match(

    resume,

    job_description

)

print(result)