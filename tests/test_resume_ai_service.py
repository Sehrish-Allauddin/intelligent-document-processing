from src.services.resume_ai_service import ResumeAIService

resume = {

    "skills": [

        "Python",

        "SQL",

        "Machine Learning",

        "TensorFlow"

    ]

}

job_description = """

We are looking for

Python
SQL
Docker
AWS
Machine Learning

"""

service = ResumeAIService()

result = service.analyze(

    resume,

    job_description

)

print(result)