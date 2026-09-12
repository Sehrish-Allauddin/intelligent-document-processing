from src.extraction.experience_parser import ExperienceParser


parser = ExperienceParser()

text = """Private Tutor
Home & Online Tutor Physics & Mathematics
2021
2026
Provided one-to-one and small-group tutoring in Physics and Mathematics.
Taught students at home as well as through online classes
Prepared students for school/college examinations, tests, and assignments
"""

result = parser.parse(text)

print("\nEXPERIENCE COUNT =", len(result))

for i, item in enumerate(result, 1):

    print("\nEXPERIENCE", i)
    print("COMPANY:", item.get("company"))
    print("JOB TITLE:", item.get("job_title"))
    print("DURATION:", item.get("duration"))
    print("DESCRIPTION:")

    for line in item.get("description", []):
        print("-", line)