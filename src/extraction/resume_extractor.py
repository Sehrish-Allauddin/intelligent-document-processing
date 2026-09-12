from email.mime import text
import re
from tracemalloc import start

from shapely import area
from src.extraction.base_extractor import BaseExtractor
from src.extraction.resume_parser import ResumeParser
from src.extraction.skill_matcher import SkillMatcher
from src.extraction.education_parser import EducationParser
from src.extraction.experience_parser import ExperienceParser
from src.extraction.project_parser import ProjectParser
from src.ner.entity_extractor import EntityExtractor
from src.ats.ats_scorer import ATSScorer
from src.extraction.resume_normalizer import ResumeNormalizer


class ResumeExtractor(BaseExtractor):

    def __init__(self):

        print("=" * 60)
        print("RESUME EXTRACTOR INITIALIZED")
        print("=" * 60)

        self.parser = ResumeParser()
        self.normalizer = ResumeNormalizer()
        self.skills = SkillMatcher()
        self.education = EducationParser()
        self.experience = ExperienceParser()
        self.projects = ProjectParser()
        self.ner = EntityExtractor()
        self.ats = ATSScorer()

    # --------------------------------------------------
    # SAFE ENTITY HELPER
    # --------------------------------------------------

    @staticmethod
    def get_entity(entities, label):

        if not isinstance(entities, list):
            return None

        for entity in entities:

            if not isinstance(entity, dict):
                continue

            if entity.get("label") == label:

                value = entity.get("text")

                if value:
                    return value

        return None

    # --------------------------------------------------
    # SAFE OCR TEXT BUILDER
    # --------------------------------------------------

    @staticmethod
    def build_text(ocr_results):

        if not isinstance(ocr_results, list):
            return ""

        lines = []

        for item in ocr_results:

            if not isinstance(item, dict):
                continue

            text = item.get("text")

            if text is None:
                continue

            text = str(text).strip()

            if text:
                lines.append(text)

        return "\n".join(lines)

    # --------------------------------------------------
    # REGEX ENTITY EXTRACTION
    # --------------------------------------------------

    def extract_regex_entities(self, text):

        result = {
            "name": None,
            "email": None,
            "phone": None,
            "linkedin": None,
            "github": None,
            "website": None
        }

        if not text:
            return result
        
        lines = [
        line.strip()
        for line in str(text).splitlines()
        if line.strip()
        ]

        # EMAIL
        email = re.search(
            r"[A-Za-z0-9._%+-]+"
            r"@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
            text,
            re.IGNORECASE
        )

        if email:
            result["email"] = email.group(0)

        # ============================================================
        # PHONE
        # ============================================================
        # Prefer Pakistani mobile formats and never treat CNIC/date as phone.
        phone_patterns = [
            r"(?<!\d)\+92[\s\-]?(?:3\d{2})[\s\-]?\d{3}[\s\-]?\d{4}(?!\d)",
            r"(?<!\d)0(?:3\d{2})[\s\-]?\d{3}[\s\-]?\d{4}(?!\d)",
        ]

        phone = None

        # Prefer lines explicitly labelled Phone/Mobile/Contact.
        for line in lines:
            line_lower = line.lower().strip()
            if any(label in line_lower for label in
                   ["phone", "mobile", "telephone", "tel", "contact"]):
                for pattern in phone_patterns:
                    match = re.search(pattern, line)
                    if match:
                        phone = match.group(0).strip()
                        break
            if phone:
                break

        # Fallback: search full OCR text.
        if not phone:
            for pattern in phone_patterns:
                match = re.search(pattern, text)
                if match:
                    phone = match.group(0).strip()
                    break

        # Final safety: reject CNIC-like values and obviously invalid numbers.
        if phone:
            digits = re.sub(r"\D", "", phone)
            if digits.startswith("92"):
                local_digits = "0" + digits[2:]
            else:
                local_digits = digits
            if (
                len(local_digits) != 11
                or not local_digits.startswith("03")
            ):
                phone = None

        result["phone"] = phone

        # LINKEDIN
        # OCR frequently changes:
        #   linkedin.com/in/name
        # into:
        #   linkedin.cominname / linkedin.comlinname / www\.linkedin...
        linkedin = re.search(
            r"(?:https?://)?(?:www[\\.]?\\s*)?"
            r"linkedin[\\./\\s]*com"
            r"(?:[\\/]?(?:in|pub|profile)[\\/]?)?"
            r"([A-Za-z0-9._-]{3,100})?",
            text,
            re.IGNORECASE
        )

        if linkedin:
            raw = linkedin.group(0)
            # Clean OCR escape characters and whitespace.
            raw_clean = re.sub(r"[\\\s]+", "", raw)
            username = linkedin.group(1) or ""
            # Fix OCR prefix accidentally attached to LinkedIn username
            username = re.sub(
               r"(?i)^linl(?=[a-z])",
                "",
               username
            )
            # If OCR swallowed /in/, recover username from the tail.
            if not username:
              m = re.search(
                  r"linkedin\.com(?:in|/in/|/pub/|pub)?([A-Za-z0-9._-]{3,100})",
                  raw_clean,
                  re.IGNORECASE
                )

              if m:
                 username = m.group(1)

            # --------------------------------------------------
            # FIX OCR "linl" PREFIX IN USERNAME
            # Example:
            # linlsehrishallauddin
            #        ↓
            # sehrishallauddin
            # --------------------------------------------------

            username = re.sub(
              r"(?i)^linl(?=[A-Za-z])",
              "",
              username
            )

            # Reject generic words accidentally captured as usernames.
            if username and username.lower() not in {
              "com",
              "in",
              "pub",
              "profile",
              "linkedin"
            }:
              result["linkedin"] = (
                 "https://www.linkedin.com/in/" + username
                )

                # GITHUB
        github = re.search(
            r"(?:https?://)?"
            r"(?:www\.)?"
            r"github\.com/[^\s]+",
            text,
            re.IGNORECASE
        )

        if github:
            result["github"] = github.group(0)

        
        # NAME
        # Prepare clean lines first because name extraction uses them.
        lines = [
            line.strip()
            for line in text.splitlines()
            if line.strip()
        ]

        # Robust name extraction: reject headings and sentence fragments.

        blocked_names = {
            "about me", "personal details", "professional summary",
            "summary", "profile", "objective", "resume",
            "curriculum vitae", "cv", "skills", "education",
            "experience", "work experience", "teaching experience",
            "projects", "certifications", "languages",
            "contact", "contacts", "mathematics", "physics",
        }

        blocked_words = {
            "is", "are", "am", "was", "were", "the", "a", "an",
            "and", "with", "for", "from", "experience",
            "professional", "dedicated", "hardworking",
            "passionate", "educator", "teacher", "student",
        }

        def valid_name(value):
            if not value:
                return False

            value = str(value).strip()
            lower = value.lower()
            words = value.split()

            if lower in blocked_names:
                return False

            if len(words) < 2 or len(words) > 4:
                return False

            for word in words:
                clean_word = re.sub(
                    r"[^A-Za-zÀ-ÿ'-]",
                    "",
                    word
                ).lower()

                if clean_word in blocked_words:
                    return False

                if not re.match(
                    r"^[A-Za-zÀ-ÿ'-]+$",
                    word
                ):
                    return False

            return True

        # FIRST: use NER only when the entity looks like a real name.
        ner_name = None
        try:
           ner_entities = self.ner.extract(text)

           if isinstance(ner_entities, list):
              for entity in ner_entities:
                 if not isinstance(entity, dict):
                    continue

                 if entity.get("label") != "PERSON":
                    continue
 
                 value = str(
                    entity.get("text", "")
                ).strip()

                 if valid_name(value):
                    ner_name = value
                    break

        except Exception as e:
           print("NER Name Error:", e)
           ner_name = None

        # SECOND: handle OCR names split across consecutive lines.
        # Example: MAHEEN / MUKHTAR / MATHEMATICS
        if not ner_name:
            for i in range(len(lines[:10]) - 1):
                first = lines[i].strip()
                second = lines[i + 1].strip()

                candidate = first + " " + second

                if valid_name(candidate):
                    ner_name = candidate.title()
                    break

        # THIRD: normal single-line name.
        if not ner_name:
            for line in lines[:10]:
                candidate = line.strip()

                if valid_name(candidate):
                    ner_name = candidate.title()
                    break

        result["name"] = ner_name

        return result

    # --------------------------------------------------
    # ROBUST FALLBACK PARSERS
    # --------------------------------------------------

    @staticmethod
    def _clean_year(value):
        value = str(value or "").strip()
        m = re.search(r"\b(?:19|20)\d{2}\s*(?:-|to|–|—)\s*(?:19|20)\d{2}\b",
                      value, re.IGNORECASE)
        if m:
            return re.sub(r"\s+", " ", m.group(0))
        m = re.search(r"\b(?:19|20)\d{2}\b", value)
        return m.group(0) if m else None

    @staticmethod
    def _is_year_line(line):
        return bool(re.search(r"\b(?:19|20)\d{2}\b", line or ""))

    @staticmethod
    def _looks_like_institution(line):
        low = (line or "").lower()
        if not line or len(line.split()) < 2:
            return False
        if low.startswith(("city:", "year:", "cgpa:", "present")):
            return False

        keywords = (
            "school", "college", "university", "academy",
            "institute", "public", "group", "system"
        )

        return any(k in low for k in keywords)

    def _fallback_education(self, text):
        """
        Generic education extractor.

        Works with different CV layouts without relying on specific
        candidate names, universities, degrees, or institutions.
        """

        if not text:
            return []

        import re

        def clean(value):
            return re.sub(r"\s+", " ", str(value or "")).strip()

        def normalize(value):
            value = clean(value).lower()
            value = re.sub(r"[^a-z0-9&+./#' -]", " ", value)
            return re.sub(r"\s+", " ", value).strip()

        lines = [
            clean(line)
            for line in str(text).splitlines()
            if clean(line)
        ]

        if not lines:
            return []

        education_headers = {
            "education",
            "educational background",
            "education background",
            "academic background",
            "academic qualifications",
            "academic history",
            "qualifications",
            "educational qualifications",
            "education & qualifications",
            "education and qualifications",
        }

        stop_headers = {
            "experience",
            "work experience",
            "professional experience",
            "employment",
            "employment history",
            "career history",
            "work history",
            "skills",
            "technical skills",
            "professional skills",
            "core skills",
            "key skills",
            "competencies",
            "expertise",
            "projects",
            "personal projects",
            "certifications",
            "certificates",
            "languages",
            "references",
            "achievements",
            "awards",
            "interests",
            "hobbies",
            "contact",
            "contacts",
            "personal details",
            "summary",
            "profile",
            "objective",
            "career objective",
            "about me",
        }

        # Broad qualification signals.
        # These are generic category words, not specific institutions.
        degree_pattern = re.compile(
            r"\b("
            r"ph\.?d|doctorate|doctoral|"
            r"master(?:'s)?|m\.?sc|m\.?a|m\.?s|mba|m\.?phil|"
            r"bachelor(?:'s)?|b\.?sc|b\.?a|b\.?s|bba|b\.?com|"
            r"associate|diploma|"
            r"higher secondary|secondary school|high school|"
            r"intermediate|matric|"
            r"foundation|certificate|certification|"
            r"llb|jd|md|mbbs|bds|pharmd|"
            r"engineering|computer science|information technology|"
            r"data science|business administration|"
            r"accounting|finance|economics|"
            r"education|arts|commerce|science"
            r")\b",
            re.I,
        )

        date_pattern = re.compile(
            r"\b(?:"
            r"(?:19|20)\d{2}\s*(?:-|–|—|to)\s*"
            r"(?:(?:19|20)\d{2}|present|current|ongoing)"
            r"|"
            r"(?:19|20)\d{2}"
            r")\b",
            re.I,
        )

        month_year_pattern = re.compile(
            r"\b(?:"
            r"jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|"
            r"may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|"
            r"sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?"
            r")\s+(?:19|20)\d{2}\b",
            re.I,
        )

        def is_date(line):
            return bool(
                date_pattern.search(line)
                or month_year_pattern.search(line)
            )

        def extract_date(line):
            match = date_pattern.search(line)
            if match:
                return clean(match.group(0))

            match = month_year_pattern.search(line)
            if match:
                return clean(match.group(0))

            return None

        # --------------------------------------------------
        # FIND EDUCATION AREA
        # --------------------------------------------------

        start = None

        for i, line in enumerate(lines):
            if normalize(line) in education_headers:
                start = i + 1
                break

        if start is not None:
            end = len(lines)

            for i in range(start, len(lines)):
                if normalize(lines[i]) in stop_headers:
                    end = i
                    break

            area = lines[start:end]

        else:
            # No heading: locate qualification evidence.
            positions = [
                i for i, line in enumerate(lines)
                if degree_pattern.search(line)
            ]

            if not positions:
                return []

            start = max(0, positions[0] - 2)

            # Continue until another strong section header.
            end = len(lines)

            for i in range(positions[-1] + 1, len(lines)):
                if normalize(lines[i]) in stop_headers:
                    end = i
                    break

            area = lines[start:end]

        if not area:
            return []

        # --------------------------------------------------
        # IDENTIFY EDUCATION RECORD ANCHORS
        # --------------------------------------------------

        degree_positions = [
            i for i, line in enumerate(area)
            if degree_pattern.search(line)
        ]

        if not degree_positions:
            return []

        records = []

        for pos_number, degree_index in enumerate(degree_positions):

            # Each qualification owns the text up to the next
            # qualification. This prevents one qualification's
            # date from leaking into another.
            next_degree = (
                degree_positions[pos_number + 1]
                if pos_number + 1 < len(degree_positions)
                else len(area)
            )

            block_start = degree_index
            block_end = next_degree

            block = area[block_start:block_end]

            if not block:
                continue

            degree = clean(area[degree_index])

            if not degree:
                continue

            # --------------------------------------------------
            # DATE
            # --------------------------------------------------

            year = None

            # First prefer dates after the degree.
            for line in block[1:]:
                candidate = extract_date(line)

                if candidate:
                    year = candidate
                    break

            # If no date follows it, allow a date immediately
            # before the degree.
            if year is None and degree_index > 0:
                previous = area[degree_index - 1]
                candidate = extract_date(previous)

                if candidate:
                    year = candidate

            # --------------------------------------------------
            # INSTITUTION
            # --------------------------------------------------

            institution = None
            institution_candidates = []

            institution_keywords = re.compile(
                r"\b("
                r"school|college|university|academy|"
                r"institute|faculty|campus|"
                r"polytechnic|department|"
                r"board|institute|centre|center"
                r")\b",
                re.I,
            )

            for relative_index, line in enumerate(block[1:], start=1):

                candidate = clean(line)

                if not candidate:
                    continue

                if is_date(candidate):
                    continue

                if normalize(candidate) in stop_headers:
                    continue

                # Do not select another qualification as institution.
                if degree_pattern.search(candidate):
                    continue

                # Long prose is more likely a description.
                if len(candidate.split()) > 10:
                    continue

                # Common academic-status sentences are not institutions.
                if re.match(
                    r"^(completed|graduated|studied|pursuing|"
                    r"currently|major|specialization|"
                    r"specialised|specialized|"
                    r"coursework|thesis|cgpa|gpa)\b",
                    candidate,
                    re.I,
                ):
                    continue

                score = 0

                if institution_keywords.search(candidate):
                    score += 5

                # Institution generally appears close to the degree.
                score += max(0, 4 - relative_index)

                # Short standalone names are plausible institution names.
                if 1 <= len(candidate.split()) <= 7:
                    score += 1

                institution_candidates.append(
                    (score, relative_index, candidate)
                )

            if institution_candidates:
                institution_candidates.sort(
                    key=lambda item: (-item[0], item[1])
                )
                institution = institution_candidates[0][2]

            # --------------------------------------------------
            # FALLBACK INSTITUTION
            # --------------------------------------------------

            # If no keyword-based institution was found, use a short
            # non-date, non-degree line immediately following the degree.
            if institution is None:

                for candidate in block[1:4]:

                    candidate = clean(candidate)

                    if not candidate:
                        continue

                    if is_date(candidate):
                        continue

                    if degree_pattern.search(candidate):
                        continue

                    if normalize(candidate) in stop_headers:
                        continue

                    if len(candidate.split()) <= 7:
                        institution = candidate
                        break

            # --------------------------------------------------
            # VALIDATION
            # --------------------------------------------------

            normalized_degree = normalize(degree)

            if normalized_degree in stop_headers:
                continue

            # Reject obvious section labels.
            if len(normalized_degree.split()) <= 1 and normalized_degree in {
                "education",
                "experience",
                "skills",
                "projects",
                "languages",
            }:
                continue

            records.append(
                {
                    "degree": degree,
                    "institution": institution,
                    "year": year,
                }
            )

        # --------------------------------------------------
        # DEDUPLICATION
        # --------------------------------------------------

        cleaned_records = []
        seen = set()

        for record in records:

            key = (
                normalize(record.get("degree")),
                normalize(record.get("institution")),
                normalize(record.get("year")),
            )

            if key in seen:
                continue

            seen.add(key)
            cleaned_records.append(record)

        return cleaned_records

    def _fallback_experience(self, text):
        if not text:
            return []
        import re
        def clean(v): return re.sub(r"\s+", " ", str(v)).strip()
        def norm(v):
            v=clean(v).lower()
            return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9&+./#' -]", " ", v)).strip()
        lines=[clean(x) for x in str(text).splitlines() if clean(x)]
        if not lines: return []
        exp_headers={"experience","work experience","professional experience","employment","employment history","employment experience","career history","work history","professional background","professional history","career experience","job experience","work background","internship","internships","internship experience","industrial experience","teaching experience","relevant experience","relevant work experience","work experience and internships"}
        stop_headers={"education","educational background","academic background","academic qualifications","qualifications","skills","technical skills","professional skills","core skills","key skills","competencies","expertise","projects","personal projects","certifications","certificates","languages","references","achievements","awards","interests","hobbies","contact","contacts","personal details","profile","summary","about me","objective","career objective"}
        date_re=re.compile(r"\b(?:19|20)\d{2}\s*(?:[-–—]|to)\s*(?:(?:19|20)\d{2}|present|current|ongoing)\b|\b(?:19|20)\d{2}\b|\b(?:present|current|ongoing)\b",re.I)
        month_re=re.compile(r"\b(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:t(?:ember)?)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)\s+(?:19|20)\d{2}\b",re.I)
        title_re=re.compile(r"\b(developer|engineer|architect|analyst|scientist|programmer|designer|researcher|consultant|manager|supervisor|coordinator|administrator|assistant|officer|executive|director|lead|specialist|associate|intern|trainee|teacher|tutor|lecturer|professor|instructor|accountant|auditor|advisor|agent|representative|technician|nurse|doctor|pharmacist|lawyer|writer|editor|journalist|marketer|sales|operations|hr|human resources|product manager|project manager|data analyst|data scientist|software engineer)\b",re.I)
        action_re=re.compile(r"^(provided|managed|developed|created|designed|implemented|prepared|taught|trained|assisted|responsible|handled|worked|maintained|analyzed|supported|coordinated|supervised|conducted|delivered|performed|helped|monitored|explained|planned|organized|achieved|built|led|served|administered|researched|consulted|optimized|automated|deployed|contributed|collaborated|facilitated|mentored|executed|improved)\b",re.I)
        org_re=re.compile(r"\b(school|college|university|academy|institute|company|organization|corporation|hospital|bank|group|system|center|centre|agency|firm|solutions|technology|technologies|limited|ltd|llc|inc|studio|services|clinic|laboratory|lab|foundation|department|office|association)\b",re.I)

        start=next((i+1 for i,x in enumerate(lines) if norm(x) in exp_headers),None)
        if start is not None:
            end=next((i for i in range(start+1,len(lines)) if norm(lines[i]) in stop_headers),len(lines))
            area=lines[start:end]
        else:
            anchors=[]
            for i,x in enumerate(lines):
                if date_re.search(x) or month_re.search(x):
                    nearby=" ".join(lines[max(0,i-3):min(len(lines),i+5)])
                    if title_re.search(nearby) or action_re.search(nearby): anchors.append(i)
            if not anchors: return []
            area=lines[max(0,min(anchors)-3):min(len(lines),max(anchors)+7)]
        if not area: return []

        date_idx=[i for i,x in enumerate(area) if date_re.search(x) or month_re.search(x)]
        regions=[]
        if date_idx:
            groups=[[date_idx[0]]]
            for idx in date_idx[1:]:
                if idx-groups[-1][-1]<=2: groups[-1].append(idx)
                else: groups.append([idx])
            for n,g in enumerate(groups):
                nxt=groups[n+1][0] if n+1<len(groups) else len(area)
                regions.append(area[max(0,g[0]-3):nxt])
        else: regions=[area]

        records=[]
        for block in regions:
            text_block=" ".join(block)
            has_date=bool(date_re.search(text_block) or month_re.search(text_block))
            has_title=bool(title_re.search(text_block))
            has_action=any(action_re.search(x) for x in block)
            if not ((has_date and (has_title or has_action)) or (start is not None and has_title)): continue

            duration=None
            m=re.search(r"\b(?:19|20)\d{2}\s*(?:[-–—]|to)\s*(?:(?:19|20)\d{2}|present|current|ongoing)\b",text_block,re.I)
            if m: duration=clean(m.group())
            else:
                months=month_re.findall(text_block); years=re.findall(r"\b(?:19|20)\d{2}\b",text_block)
                if len(months)>=2: duration=f"{months[0]} - {months[1]}"
                elif len(years)>=2: duration=f"{years[0]} - {years[1]}"
                elif len(years)==1: duration=years[0]
                else:
                    m=re.search(r"\b(present|current|ongoing)\b",text_block,re.I)
                    if m: duration=m.group()

            title_candidates=[]; company_candidates=[]
            for i,raw in enumerate(block):
                line=clean(raw); no_date=clean(month_re.sub("",date_re.sub("",line)))
                if not no_date or norm(no_date) in stop_headers|exp_headers: continue
                if action_re.search(no_date) or len(no_date.split())>10: continue
                if title_re.search(no_date): title_candidates.append((i,no_date))
                if org_re.search(no_date): company_candidates.append((i,no_date))

            job_title=None
            if title_candidates:
                title_candidates.sort(key=lambda x:(len(x[1].split()),x[0])); job_title=title_candidates[0][1]

            if not job_title:
                dp=next((i for i,x in enumerate(block) if date_re.search(x) or month_re.search(x)),None)
                if dp is not None:
                    for i in range(dp-1,max(-1,dp-4),-1):
                        c=clean(month_re.sub("",date_re.sub("",block[i])))
                        if c and not action_re.search(c) and len(c.split())<=8 and norm(c) not in stop_headers|exp_headers:
                            job_title=c; break

            company=None
            valid=[(i,c) for i,c in company_candidates if not job_title or norm(c)!=norm(job_title)]
            if valid:
                anchor=next((i for i,x in enumerate(block) if job_title and norm(x)==norm(job_title)),0)
                valid.sort(key=lambda x:(abs(x[0]-anchor),len(x[1]))); company=valid[0][1]

            if not company and job_title:
                ti=next((i for i,x in enumerate(block) if norm(x)==norm(job_title)),None)
                if ti is not None:
                    for i in range(ti+1,min(len(block),ti+4)):
                        c=clean(month_re.sub("",date_re.sub("",block[i])))
                        if c and not action_re.search(c) and len(c.split())<=8 and norm(c) not in stop_headers|exp_headers:
                            company=c; break

            description=[]
            for line in block:
                c=clean(line)
                if not c or (job_title and norm(c)==norm(job_title)) or (company and norm(c)==norm(company)): continue
                if date_re.fullmatch(c) or month_re.fullmatch(c) or norm(c) in stop_headers|exp_headers: continue
                if 3<=len(c.split())<=35 and action_re.search(c): description.append(c)

            if job_title or company or duration or description:
                records.append({"company":company,"job_title":job_title,"duration":duration,"description":description})

        seen=set(); out=[]
        for r in records:
            key=(norm(r.get("company") or ""),norm(r.get("job_title") or ""),norm(r.get("duration") or ""),tuple(norm(x) for x in r.get("description") or []))
            if key not in seen:
                seen.add(key); out.append(r)
        return out

    def extract(self, ocr_results):

        print("\n" + "=" * 60)
        print("RESUME EXTRACTION STARTED")
        print("=" * 60)

        # --------------------------------------------------
        # OCR
        # --------------------------------------------------

        full_text = self.build_text(
            ocr_results
        )

        print("\nOCR TEXT LENGTH:")
        print(len(full_text))

        # --------------------------------------------------
        # NORMALIZATION
        # --------------------------------------------------

        try:

            normalized = self.normalizer.normalize(
                full_text
            )

            if normalized is not None:
                full_text = normalized

        except Exception as e:

            print(
                "Normalization Error:",
                e
            )

        if not full_text:
            full_text = ""

        # --------------------------------------------------
        # PARSE SECTIONS
        # --------------------------------------------------

        try:

            sections = self.parser.parse(
                full_text
            )

        except Exception as e:

            print(
                "Resume Parser Error:",
                e
            )

            sections = {}

        if not isinstance(sections, dict):
            sections = {}

        # --------------------------------------------------
        # REGEX ENTITIES
        # --------------------------------------------------

        regex_entities = (
            self.extract_regex_entities(
                full_text
            )
        )

        if not isinstance(
            regex_entities,
            dict
        ):
            regex_entities = {}

        # --------------------------------------------------
        # NER
        # --------------------------------------------------

        try:

            ner_entities = self.ner.extract(
                full_text
            )

        except Exception as e:

            print(
                "NER Error:",
                e
            )

            ner_entities = []

        if not isinstance(
            ner_entities,
            list
        ):
            ner_entities = []

        # --------------------------------------------------
        # BASIC DATA
        # --------------------------------------------------

        data = {

            "document_type": "resume",

            "name": (
                regex_entities.get("name")
                or self.get_entity(
                    ner_entities,
                    "PERSON"
                )
            ),

            "email": (
                regex_entities.get("email")
                or self.get_entity(
                    ner_entities,
                    "EMAIL"
                )
            ),

            "phone": (
                regex_entities.get("phone")
                or self.get_entity(
                    ner_entities,
                    "PHONE"
                )
            ),

            "address": self.get_entity(
                ner_entities,
                "GPE"
            ),

            "linkedin": regex_entities.get(
                "linkedin"
            ),

            "github": regex_entities.get(
                "github"
            ),

            "website": regex_entities.get(
                "website"
            ),

            "summary": "",

            "skills": [],

            "education": [],

            "experience": [],

            "projects": [],

            "certifications": [],

            "languages": [],

            "statistics": {},

            "raw_text": full_text
        }

        # --------------------------------------------------
        # LINKEDIN FALLBACK / OCR NORMALIZATION
        # --------------------------------------------------

        linkedin = data.get("linkedin")

        if linkedin:
           linkedin = str(linkedin).strip()

           # Remove backslashes / OCR noise
           linkedin = linkedin.replace("\\", "")
           linkedin = linkedin.replace(" ", "")
           linkedin = linkedin.rstrip(".,;:)")

           # ----------------------------------------------
           # FIX COMMON OCR ERRORS
           # ----------------------------------------------

           # linkedin.comlinlUSERNAME
           linkedin = re.sub(
              r"(?i)linkedin\.comlinl",
               "linkedin.com/in/",
                linkedin
            )

           # linkedin.cominUSERNAME
           linkedin = re.sub(
              r"(?i)linkedin\.comin(?=[A-Za-z0-9_-])",
             "linkedin.com/in/",
              linkedin
            )

           # linkedin.com/inlUSERNAME
           linkedin = re.sub(
             r"(?i)linkedin\.com/inl",
             "linkedin.com/in/",
              linkedin
            )

           # ----------------------------------------------
           # Remove OCR "linl" from username
           #
           # /in/linlsehrishallauddin
           #       ↓
           # /in/sehrishallauddin
           # ----------------------------------------------

           linkedin = re.sub(
              r"(?i)(linkedin\.com/in/)linl(?=[A-Za-z0-9_-]+)",
              r"\1",
              linkedin
            )

            # ----------------------------------------------
            # ADD HTTPS
            # ----------------------------------------------

           if linkedin.lower().startswith("www.linkedin.com"):
              linkedin = "https://" + linkedin

           elif linkedin.lower().startswith("linkedin.com"):
              linkedin = "https://" + linkedin

            # ----------------------------------------------
            # EXTRACT ONLY VALID LINKEDIN URL
            # ----------------------------------------------

           match = re.search(
             r"(?i)(https?://(?:www\.)?linkedin\.com/in/[A-Za-z0-9_-]+)",
             linkedin
            )

           if match:
             linkedin = match.group(1)
           else:
              linkedin = None

        data["linkedin"] = linkedin

        # --------------------------------------------------
        # SUMMARY
        # --------------------------------------------------

        summary = sections.get(
            "summary",
            []
        )

        if not isinstance(
            summary,
            list
        ):
            summary = []

        data["summary"] = "\n".join(summary[:8])

        # If ABOUT ME was interrupted by a PERSONAL DETAILS heading, recover
        # the prose between ABOUT ME and the next major resume section.
        if not data["summary"].strip():
            lines_for_summary = [
                line.strip()
                for line in full_text.splitlines()
                if line.strip()
            ]
            start = None
            end = len(lines_for_summary)

            for i, line in enumerate(lines_for_summary):
                if line.lower().strip() == "about me":
                    start = i + 1
                    break

            if start is not None:
                for i in range(start, len(lines_for_summary)):
                    if lines_for_summary[i].lower().strip() in {
                        "teaching experience",
                        "experience",
                        "professional experience",
                        "work experience",
                    }:
                        end = i
                        break

                personal_labels = {
                    "personal details",
                    "father name:",
                    "date of birth:",
                    "cnic:",
                    "gender:",
                    "religion:",
                    "marital status:",
                }

                summary_parts = []
                skip_value = False

                for line in lines_for_summary[start:end]:
                    lower = line.lower().strip()

                    if lower in personal_labels:
                        skip_value = True
                        continue

                    if skip_value:
                        skip_value = False
                        # Keep actual prose, skip short personal-detail values.
                        if len(line.split()) <= 3:
                            continue

                    if "@" in line:
                        continue

                    if re.fullmatch(r"\+?[\d\s()\-]+", line):
                        continue

                    if lower in {"contact", "contacts"}:
                        continue

                    summary_parts.append(line)

                data["summary"] = " ".join(summary_parts)

        # --------------------------------------------------
        # SKILLS
        # --------------------------------------------------

        try:

            skills = self.skills.extract(
                full_text
            )

        except Exception as e:

            print(
                "Skills Error:",
                e
            )

            skills = []

        if not isinstance(
            skills,
            list
        ):
            skills = []

        data["skills"] = sorted(
            set(skills)
        )

        # --------------------------------------------------
        # EDUCATION
        # --------------------------------------------------

        try:
           education = self._fallback_education(full_text)
        except Exception as e:
           print("Fallback Education Error:", e)
           education = []

        if not education:
           try:
             education = self.education.parse(full_text)
           except Exception as e:
            print("Education Parser Error:", e)
            education = []

        if not isinstance(education, list):
          education = []

        data["education"] = education

        # --------------------------------------------------
        # EXPERIENCE
        # --------------------------------------------------

        try:
           experience = self._fallback_experience(full_text)
        except Exception as e:
          print("Fallback Experience Error:", e)
          experience = []

        if not experience:
           try:
              experience_text = "\n".join(
                 sections.get("experience", [])
               )

              experience = self.experience.parse(
                 experience_text
               )
           except Exception as e:
              print("Experience Parser Error:", e)
              experience = []

        if not isinstance(experience, list):
         experience = []

        # Remove invalid / garbage experience records
        valid_experience = []

        for item in experience:
          if not isinstance(item, dict):
            continue

          company = item.get("company")
          job_title = item.get("job_title")
          duration = item.get("duration")
          description = item.get("description")

          # Keep only records containing meaningful information
          if (
             company
             or duration
             or (
                isinstance(job_title, str)
                and len(job_title.strip()) >= 4
                and job_title.lower().strip()
                not in {
                  "strong - communication",
                  "strong communication",
                  "communication",
                  "experience",
               }
           )
           or (
              isinstance(description, list)
              and len(description) > 0
           )
        ):
           valid_experience.append(item)

        # If parser failed or produced garbage,
        # use generic OCR-based fallback.
        if not valid_experience:

           try:
              fallback_text = (
                data.get("raw_text")
                or data.get("ocr_text")
                or "\n".join(
                   sections.get("experience", [])
                )
              )

              experience = self._fallback_experience(
               fallback_text
              )

           except Exception as e:

             print(
                "Experience Fallback Error:",
                 e
              )

             experience = []

        else:

          experience = valid_experience

        data["experience"] = experience

        # --------------------------------------------------
        # PROJECTS
        # --------------------------------------------------

        project_lines = sections.get(
            "projects",
            []
        )

        if not isinstance(
            project_lines,
            list
        ):
            project_lines = []

        print("\nPROJECT SECTION BEFORE PARSER:")

        for line in project_lines:

            print(
                "PROJECT LINE:",
                repr(line)
            )

        try:

            projects = self.projects.parse(
                project_lines
            )

        except Exception as e:

            print(
                "Projects Error:",
                e
            )

            projects = []

        if not isinstance(
            projects,
            list
        ):
            projects = []

        data["projects"] = projects

        # --------------------------------------------------
        # FINAL PROJECT CLEANUP
        # --------------------------------------------------

        clean_projects = []

        for project in data.get("projects", []):

            if not isinstance(project, dict):
                continue

            title = str(project.get("title", "")).strip()
            if not title:
                continue

            description = project.get("description", [])
            if not isinstance(description, list):
                description = [str(description)]

            description = [
                str(item).strip()
                for item in description
                if str(item).strip()
            ]

            clean_projects.append({
                "title": title,
                "description": description
            })

        data["projects"] = clean_projects

        print("\nPROJECTS AFTER CLEANUP:")

        for project in data["projects"]:

            print(
                "PROJECT:",
                project.get("title")
            )
        # --------------------------------------------------
        # CERTIFICATIONS
        # --------------------------------------------------

        certifications = []

        for line in sections.get(
            "certifications",
            []
        ):

            if not isinstance(
                line,
                str
            ):
                continue

            line = line.strip()

            if line:
                certifications.append(
                    line
                )

        data["certifications"] = list(
            dict.fromkeys(
                certifications
            )
        )

        # --------------------------------------------------
        # LANGUAGES
        # --------------------------------------------------

        # Extract languages from the LANGUAGES section only.
        # This prevents education/degree/institution lines from being
        # incorrectly added to the languages list.

        common_languages = {
            "english", "urdu", "pushto", "pashto", "hindi", "punjabi",
            "arabic", "persian", "farsi", "bengali", "sindhi",
            "german", "french", "spanish", "italian", "chinese",
            "mandarin", "japanese", "korean", "russian", "turkish",
        }

        section_headers = {
            "education",
            "experience",
            "work experience",
            "professional experience",
            "teaching experience",
            "skills",
            "projects",
            "certifications",
            "references",
            "contact",
            "contacts",
            "about me",
            "summary",
            "professional summary",
        }

        language_candidates = []

        language_start = None
        text_lines = [
            line.strip()
            for line in full_text.splitlines()
            if line.strip()
        ]

        # Find the LANGUAGES heading.
        for i, line in enumerate(text_lines):
            if line.lower().strip() in {
                "language",
                "languages",
                "language skills",
                "languages skills",
            }:
                language_start = i + 1
                break

        if language_start is not None:

            for line in text_lines[language_start:]:

                clean = line.strip()
                lower_line = clean.lower()

                # Stop at the next major section.
                if lower_line in section_headers:
                    break

                # OCR may put multiple languages on one line.
                parts = re.split(r"[,/|;]+", clean)

                for part in parts:

                    candidate = part.strip()
                    normalized = candidate.lower()

                    if normalized in common_languages:

                        if normalized in {"pashto", "pushto"}:
                            value = "Pushto"
                        else:
                            value = candidate.title()

                        if value not in language_candidates:
                            language_candidates.append(value)

        data["languages"] = language_candidates

        # --------------------------------------------------
        # STATISTICS
        # --------------------------------------------------

        lines = [
            line.strip()
            for line in full_text.split("\n")
            if line.strip()
        ]

        data["statistics"] = {

            "total_lines": len(lines),

            "entities_found": len(
                ner_entities
            ),

            "skills_found": len(
                data["skills"]
            ),

            "education_records": len(
                data["education"]
            ),

            "experience_records": len(
                data["experience"]
            ),

            "projects": len(
                data["projects"]
            ),

            "certifications": len(
                data["certifications"]
            ),

            "languages": len(
                data["languages"]
            )
        }

        # --------------------------------------------------
        # CLEAN PROJECTS
        # --------------------------------------------------
        
        clean_projects = []
        
        for project in data.get("projects", []):
        
            if not isinstance(project, dict):
                continue
        
            title = str(project.get("title", "")).strip()
        
            if not title:
                continue
        
            description = project.get("description", [])
        
            if not isinstance(description, list):
                description = [str(description)]
        
            description = [
                str(x).strip()
                for x in description
                if str(x).strip()
            ]
        
            clean_projects.append({
                 "title": title,
                "description": description
                })
        
        data["projects"] = clean_projects

        # --------------------------------------------------
        # FINAL LINKEDIN CLEANUP
        # --------------------------------------------------

        linkedin = data.get("linkedin")

        if linkedin:
          linkedin = str(linkedin).strip()

          # Remove spaces and OCR backslashes
          linkedin = linkedin.replace("\\", "")
          linkedin = linkedin.replace(" ", "")

          # ----------------------------------------------
          # Find LinkedIn username from ANY LinkedIn URL
          # ----------------------------------------------

          match = re.search(
             r"linkedin\.com/in/([^/?#\s]+)",
             linkedin,
             re.IGNORECASE
            )

          if match:

             username = match.group(1)

            # OCR commonly adds "linl" at the beginning
            # Example:
            # linlsehrishallauddin
            #       ↓
            # sehrishallauddin

             username = re.sub(
              r"(?i)^linl",
              "",
              username
            )

            # Remove accidental punctuation
             username = username.strip(".,;:)")

             if username:

              data["linkedin"] = (
                  "https://www.linkedin.com/in/"
                  + username
                )

             else:

               data["linkedin"] = None

          else:

            data["linkedin"] = None

        else:

          data["linkedin"] = None

        # --------------------------------------------------
        # EDUCATION FALLBACK
        # Recover missing education records from raw OCR text
        # --------------------------------------------------

        raw_text = data.get("raw_text", "")

        if raw_text:

           lines = [
              re.sub(r"\s+", " ", str(line)).strip()
              for line in raw_text.splitlines()
            ]

           # Find EDUCATION section
           start = None
           end = None

           for i, line in enumerate(lines):

               if line.upper() == "EDUCATION":
                 start = i + 1
                 break

           if start is not None:

             for i in range(start, len(lines)):

               if lines[i].upper() in {
                  "LANGUAGES",
                  "CERTIFICATIONS",
                  "EXPERIENCE",
                  "SKILLS",
                  "PROJECTS"
                }:
                  end = i
                  break

             if end is None:
               end = len(lines)

             education_lines = lines[start:end]

             degree_pattern = re.compile(
                 r"(?i)\b("
                 r"matric|intermediate|bachelor|master|"
                 r"phd|doctorate|diploma|associate|"
                 r"b\.?s\.?|m\.?s\.?|bsc|msc|"
                 r"bba|mba|bed|m\.?ed"
                 r")\b"
                )

             year_pattern = re.compile(
                 r"\b(?:19|20)\d{2}"
                 r"(?:\s*(?:to|-|–)\s*(?:19|20)\d{2})?\b"
                )

             fallback_education = []

             for i, line in enumerate(education_lines):

                 if not degree_pattern.search(line):
                  continue

                 degree = line.strip()

                 institution = None
                 year = None

                 # Search following lines for institution/year
                 for j in range(i + 1, min(i + 6, len(education_lines))):

                   candidate = education_lines[j].strip()

                   if not candidate:
                       continue

                   # Year
                   year_match = year_pattern.search(candidate)

                   if year_match:
                      year = year_match.group(0)

                      if candidate.lower() in {
                          "present",
                          "current"
                        }:
                          year = "Present"

                      continue

                   if candidate.lower() in {
                      "city: peshawar",
                      "city: swabi",
                      "city: islamabad",
                      "present",
                      "current"
                 }:
                     continue

                    # First useful text after degree = institution
                     if institution is None:
                       institution = candidate

                 # Look separately for Present
             for j in range(i + 1, min(i + 6, len(education_lines))):
                 if education_lines[j].lower() in {
                     "present",
                     "current"
                  }:
                    if year:
                        year = year + " - Present"
                    else:
                        year = "Present"

                 if degree and institution:

                  record = {
                      "degree": degree,
                      "institution": institution,
                      "year": year
                    }
                  fallback_education.append(record)

             # Merge without duplicates
             existing = data.get("education", [])

             if not isinstance(existing, list):
               existing = []

             merged = []

             for item in existing + fallback_education:

               if not isinstance(item, dict):
                 continue

               degree = str(
                  item.get("degree", "")
                ).strip()

               institution = str(
                item.get("institution", "")
               ).strip()

               if not degree or not institution:
                  continue

               duplicate = False

               for old in merged:

                if (
                    old["degree"].lower()
                    == degree.lower()
                    and
                    old["institution"].lower()
                    == institution.lower()
                ):
                    duplicate = True
                    break

               if not duplicate:
                merged.append({
                    "degree": degree,
                    "institution": institution,
                    "year": item.get("year")
                })

        data["education"] = merged

        # --------------------------------------------------
        # CLEAN CERTIFICATIONS
        # --------------------------------------------------

        invalid_certifications = {
          "using",
          "use",
          "and",
          "with",
          "from",
          "the",
          "to",
          "for",
          "present",
        }

        clean_certifications = []

        for cert in data.get("certifications", []):

            cert = str(cert).strip()

            if not cert:
               continue

            if cert.lower() in invalid_certifications:
              continue

            clean_certifications.append(cert)

        data["certifications"] = clean_certifications

        
        # --------------------------------------------------
        # ATS
        # --------------------------------------------------

        try:

            ats = self.ats.score(
                data
            )

        except Exception as e:

            print(
                "ATS Error:",
                e
            )

            ats = {
                "overall_score": 0,
                "breakdown": {},
                "recommendations": []
            }

        if not isinstance(
            ats,
            dict
        ):

            ats = {
                "overall_score": 0,
                "breakdown": {},
                "recommendations": []
            }

        # --------------------------------------------------
        # SAFETY: ATS SCORE MUST NEVER EXCEED 100
        # --------------------------------------------------

        try:

            score = ats.get(
                "overall_score",
                0
            )

            score = float(score)

            ats["overall_score"] = min(
                100,
                max(0, round(score))
            )

        except Exception:

            ats["overall_score"] = 0

        data["ats"] = ats

        # --------------------------------------------------
        # FINAL DEBUG
        # --------------------------------------------------

        print("\n" + "=" * 60)
        print("FINAL RESUME RESULT")
        print("=" * 60)

        print("NAME:", data["name"])
        print("EMAIL:", data["email"])
        print("PHONE:", data["phone"])
        print("LINKEDIN:", data["linkedin"])
        print("GITHUB:", data["github"])
        print("SKILLS:", data["skills"])
        print("EDUCATION:", data["education"])
        print("EXPERIENCE:", data["experience"])
        print("PROJECTS:", data["projects"])
        print("CERTIFICATIONS:", data["certifications"])
        print("LANGUAGES:", data["languages"])
        print("STATISTICS:", data["statistics"])
        print("ATS:", data["ats"])

        print("=" * 60)

        return data
