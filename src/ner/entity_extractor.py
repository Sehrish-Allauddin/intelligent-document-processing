import re


class EntityExtractor:
    """
    Production-ready lightweight entity extractor.

    Uses regex and heuristics instead of spaCy,
    making it portable on Windows systems where
    spaCy DLLs may be blocked.
    """

    CITIES = [
        "Karachi",
        "Lahore",
        "Islamabad",
        "Rawalpindi",
        "Peshawar",
        "Quetta",
        "Multan",
        "Faisalabad",
        "Hyderabad",
        "Sialkot",
        "Gujranwala",
        "Bahawalpur",
        "London",
        "Dubai",
        "New York",
        "Toronto"
    ]

    def extract(self, text):

        entities = []
        seen = set()

        lines = [
            line.strip()
            for line in text.split("\n")
            if line.strip()
        ]

        # ---------------------------------
        # Candidate Name
        # ----------------------------------

        lines = [
           line.strip()
           for line in text.split("\n")
           if line.strip()
       ]

        ignore_words = {

           "resume",
           "curriculum vitae",
           "summary",
           "professional summary",
           "profile",
           "experience",
           "education",
           "skills",
           "projects",
           "certifications",
           "languages",
           "interests",
           "objective",
           "highlights",
           "additional information",

         # Common job titles
           "accountant",
           "financial accountant",
           "software engineer",
           "data scientist",
           "developer",
           "manager",
           "analyst"

       }

        for line in lines[:20]:

          candidate = line.strip()

          lower = candidate.lower()

          if lower in ignore_words:
              continue

          # Ignore numbers
          if any(ch.isdigit() for ch in candidate):
             continue

          # Ignore email
          if "@" in candidate:
             continue

          # Ignore URL
          if "http" in lower or "www." in lower:
             continue

          words = candidate.split()

          if len(words) < 2:
             continue

          if len(words) > 4:
             continue

          # Every word should start with uppercase
          if not all(word[0].isupper() for word in words if word):
             continue

          entities.append({

             "text": candidate,

             "label": "PERSON"

         })

          break

        # ---------------------------------
        # Email
        # ---------------------------------

        emails = re.findall(

            r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",

            text

        )

        for email in emails:

            key = ("EMAIL", email)

            if key not in seen:

                entities.append({

                    "text": email,

                    "label": "EMAIL"

                })

                seen.add(key)

        # ---------------------------------
        # Phone
        # ---------------------------------

        phones = re.findall(

            r"(\+?\d[\d\s\-()]{8,}\d)",

            text

        )

        for phone in phones:

            phone = phone.strip()

            key = ("PHONE", phone)

            if key not in seen:

                entities.append({

                    "text": phone,

                    "label": "PHONE"

                })

                seen.add(key)

        # ---------------------------------
        # LinkedIn
        # ---------------------------------

        linkedin = re.findall(

            r"(https?://)?(www\.)?linkedin\.com/in/[A-Za-z0-9_-]+",

            text,

            re.IGNORECASE

        )

        for link in linkedin:

            value = "".join(link)

            key = ("LINKEDIN", value)

            if key not in seen:

                entities.append({

                    "text": value,

                    "label": "LINKEDIN"

                })

                seen.add(key)

        # ---------------------------------
        # GitHub
        # ---------------------------------

        github = re.findall(

            r"(https?://)?(www\.)?github\.com/[A-Za-z0-9_-]+",

            text,

            re.IGNORECASE

        )

        for link in github:

            value = "".join(link)

            key = ("GITHUB", value)

            if key not in seen:

                entities.append({

                    "text": value,

                    "label": "GITHUB"

                })

                seen.add(key)

        # ---------------------------------
        # Website
        # ---------------------------------

        websites = re.findall(

            r"https?://[^\s]+",

            text

        )

        for site in websites:

            key = ("WEBSITE", site)

            if key not in seen:

                entities.append({

                    "text": site,

                    "label": "WEBSITE"

                })

                seen.add(key)

        # ---------------------------------
        # Locations
        # ---------------------------------

        lower = text.lower()

        for city in self.CITIES:

            if city.lower() in lower:

                key = ("GPE", city)

                if key not in seen:

                    entities.append({

                        "text": city,

                        "label": "GPE"

                    })

                    seen.add(key)

        # ---------------------------------
        # Organization
        # ---------------------------------

        org_patterns = [

            r".*University.*",

            r".*College.*",

            r".*Institute.*",

            r".*Company.*",

            r".*Ltd.*",

            r".*Limited.*"

        ]

        for line in lines:

            for pattern in org_patterns:

                if re.match(

                    pattern,

                    line,

                    re.IGNORECASE

                ):

                    key = ("ORG", line)

                    if key not in seen:

                        entities.append({

                            "text": line,

                            "label": "ORG"

                        })

                        seen.add(key)

                    break

        return entities