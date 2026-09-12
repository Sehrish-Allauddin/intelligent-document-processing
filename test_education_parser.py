from src.extraction.education_parser import EducationParser


parser = EducationParser()

text = """Matric (Science)
The Khyber Islamic Public School Swabi
City: Swabi
Year: 2016 to 2018
Intermediate (Engineering)
The Reader Group of School and College
Year: 2018 to 2020
Bachelor of Science (Mathematics)
Islamia College Peshawar
City: Peshawar
Year: 2020 to 2024
Bachelor of Education
University of Peshawar
Present
Year: 2026
"""

result = parser.parse(text)

print("\nEDUCATION COUNT =", len(result))

for i, item in enumerate(result, 1):

    print("\nEDUCATION", i)
    print("DEGREE:", item.get("degree"))
    print("INSTITUTION:", item.get("institution"))
    print("YEAR:", item.get("year"))