from src.extraction.skill_matcher import SkillMatcher


matcher = SkillMatcher()

text = """
MAHEEN MUKHTAR
Mathematics and Physics

Provided one-to-one and small-group tutoring
in Physics and Mathematics.

Prepared students for examinations,
tests, and assignments.

Classroom Management
Lesson Planning
Student Communication
Subject Knowledge

Taught students at home and through online classes.

Monitored students' progress and provided
individual guidance.

Communication Skills
Problem Solving
Time Management
"""

result = matcher.extract(text)

print("\nSKILL COUNT =", len(result))

print("\nDETECTED SKILLS:")

for skill in result:
    print("-", skill)