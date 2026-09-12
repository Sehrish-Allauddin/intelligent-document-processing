# Intelligent Document Processing - Fixed Source Patch

This patch updates the existing `src` code based on the uploaded project and the CV extraction output.

## Main fixes

1. `src/extraction/resume_extractor.py`
   - Fixed `extract_regex_entities()` using `self` while declared as `@staticmethod`.
   - Improved phone extraction so a CNIC/date is not selected before the actual mobile number.
   - Improved summary fallback for OCR layouts.
   - Education is parsed from complete OCR text to handle two-column CVs.
   - Languages are filtered to real language names.
   - Project cleanup no longer discards valid non-AI project titles.

2. `src/extraction/education_parser.py`
   - Uses word-boundary-aware degree detection; avoids false matches such as `be` inside `Khyber`.
   - Handles OCR spelling variants such as `Bachlor` and `Mathamatics`.
   - Handles education records interleaved with language/skills text.
   - Correctly associates degree, institution and year.

3. `src/extraction/experience_parser.py`
   - Handles separate year lines (`2021`, `2026`).
   - Merges job title + specialization.
   - Avoids terminating the record at `CONTACTS` because OCR column order can split experience text.
   - Removes obvious contact spill and school-list noise.
   - Joins OCR-wrapped continuation lines.

4. `src/extraction/resume_parser.py`
   - Adds `CONTACTS` / `PERSONAL DETAILS` as section boundaries.
   - Improves section splitting.

5. `src/extraction/project_parser.py`
   - Supports more project title patterns and generic short project titles.

## Validation

The updated Python source compiles successfully with `compileall`.

For the supplied CV OCR, the extraction logic now correctly recognizes:
- Name: Maheen Mukhtar
- Phone: +92 313 1999538
- 4 education records with institutions and years
- Experience duration: 2021 - 2026
- Languages: English, Urdu, Pashto

## Installation

The ZIP contains a replacement `src` folder. Extract it into:

`C:\Intelligent-Document-Processing`

and allow Windows to overwrite the existing `src` files.

Then run your existing Streamlit command from the project root, which from your screenshot is:

`streamlit run .\streamlit_app\app.py`

Do not replace the `venv` folder.
