from pathlib import Path
import re, shutil
from datetime import datetime

FILE = Path.cwd() / "src" / "extraction" / "resume_extractor.py"
if not FILE.exists():
    raise FileNotFoundError(f"Missing: {FILE}. Run from C:\\Intelligent-Document-Processing")

src = FILE.read_text(encoding="utf-8")
backup = FILE.with_name(FILE.stem + "_backup_" + datetime.now().strftime("%Y%m%d_%H%M%S") + FILE.suffix)
shutil.copy2(FILE, backup)

def replace_method(text, name, code):
    start = text.find(f"    def {name}(")
    if start < 0:
        raise RuntimeError(f"Method not found: {name}")
    m = re.search(r"\n    def [A-Za-z_]\w*\s*\(", text[start+5:], re.M)
    end = start + 5 + m.start() if m else len(text)
    return text[:start] + code.rstrip() + "\n\n" + text[end:].lstrip("\n")

education = r'''    def _fallback_education(self, text):
        if not text:
            return []
        import re
        def clean(v): return re.sub(r"\s+", " ", str(v)).strip()
        def norm(v):
            v=clean(v).lower()
            return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9&+./#' -]", " ", v)).strip()
        lines=[clean(x) for x in str(text).splitlines() if clean(x)]
        if not lines: return []
        edu_headers={"education","educational background","education background","academic background","academic qualifications","academic history","qualifications","educational qualifications","education & qualifications"}
        stop_headers={"experience","work experience","professional experience","employment","employment history","career history","skills","technical skills","core skills","expertise","projects","personal projects","certifications","certificates","languages","references","achievements","awards","interests","hobbies","contact","contacts","personal details","summary","profile","about me","objective","career objective"}
        degree_re=re.compile(r"\b(ph\.?\s*d|doctor(?:ate)?|master(?:'s)?|m\.?\s*(?:sc|s|a|ba|com|eng|tech|ed)|bachelor(?:'s)?|b\.?\s*(?:sc|s|a|ba|com|eng|tech|ed)|associate(?:'s)?|diploma|certificate|certification|intermediate|higher secondary|secondary school|high school|matric(?:ulation)?|fsc|fa|ics|icom|a[- ]?levels?|o[- ]?levels?|acca|ca|cma|cfa|foundation)\b",re.I)
        year_re=re.compile(r"\b(?:19|20)\d{2}\b")
        range_re=re.compile(r"\b(?:19|20)\d{2}\s*(?:[-–—]|to)\s*(?:(?:19|20)\d{2}|present|current)\b",re.I)
        start=next((i+1 for i,x in enumerate(lines) if norm(x) in edu_headers),None)
        if start is not None:
            end=next((i for i in range(start+1,len(lines)) if norm(lines[i]) in stop_headers),len(lines))
            area=lines[start:end]
        else:
            hits=[i for i,x in enumerate(lines) if degree_re.search(x)]
            if not hits: return []
            area=lines[max(0,min(hits)-2):min(len(lines),max(hits)+6)]
        positions=[i for i,x in enumerate(area) if degree_re.search(x)]
        out=[]; seen=set()
        for n,pos in enumerate(positions):
            right=positions[n+1] if n+1<len(positions) else min(len(area),pos+6)
            chunk=area[max(0,pos-2):right]
            degree=clean(area[pos]); year=None
            for line in chunk:
                m=range_re.search(line)
                if m: year=clean(m.group()); break
            if year is None:
                years=year_re.findall(" ".join(chunk))
                if years: year=years[-1]
            candidates=[]
            for j,line in enumerate(chunk):
                if line==degree or year_re.search(line) or degree_re.search(line): continue
                if norm(line) in stop_headers|edu_headers: continue
                if 1<=len(line.split())<=12: candidates.append((abs((max(0,pos-2)+j)-pos),line))
            institution=None
            if candidates:
                candidates.sort(key=lambda x:(x[0],len(x[1])))
                institution=candidates[0][1]
            key=(norm(degree),norm(institution or ""),norm(year or ""))
            if key[0] and key not in seen:
                seen.add(key); out.append({"degree":degree,"institution":institution,"year":year})
        return out
'''

experience = r'''    def _fallback_experience(self, text):
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
'''

patched = replace_method(src, "_fallback_education", education)
patched = replace_method(patched, "_fallback_experience", experience)
FILE.write_text(patched, encoding="utf-8")
print("PATCH COMPLETE")
print("Updated:", FILE)
print("Backup :", backup)
