from pathlib import Path
import json
import streamlit as st

from src.pipelines.smart_document_pipeline import SmartDocumentPipeline

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


def show():

    st.error("Resume Page Loaded Successfully")

    st.title("📄 Resume Analysis")

    st.write(
        "Upload a resume and optionally paste a Job Description to perform ATS scoring and AI-based matching."
    )

    # ----------------------------------------------------
    # Resume Upload
    # ----------------------------------------------------

    uploaded = st.file_uploader(
        "Upload Resume",
        type=["pdf", "jpg", "jpeg", "png"]
    )

    # ----------------------------------------------------
    # Job Description
    # ----------------------------------------------------

    st.markdown("---")

    job_description = st.text_area(
        "📋 Paste Job Description (Optional)",
        height=200,
        placeholder="Paste the Job Description here..."
    )

    if uploaded is None:
        return

    save_path = UPLOAD_DIR / uploaded.name

    with open(save_path, "wb") as f:
        f.write(uploaded.getbuffer())

    st.success("Resume uploaded successfully!")

    pipeline = SmartDocumentPipeline()

    # Prevent stale Streamlit/Python objects during development
    import importlib
    import src.extraction.project_parser as project_parser_module

    importlib.reload(project_parser_module)

    with st.spinner("Analyzing Resume..."):

        
        st.write("Calling SmartDocumentPipeline...")
        result = pipeline.process(save_path)
        st.write("Pipeline Finished")


        # --------------------------------------------
        # JD Matching (Only if JD provided)
        # --------------------------------------------

        if (
            result.get("document_type") == "resume"
            and job_description.strip()
        ):

            ai_result = pipeline.document_pipeline.resume_ai.analyze(
                resume=result,
                job_description=job_description
            )

            result.update(ai_result)

    st.success("Analysis Completed!")

    # ----------------------------------------------------
    # Document Information
    # ----------------------------------------------------

    st.markdown("---")

    st.subheader("📄 Document Information")

    col1, col2 = st.columns(2)

    with col1:

        st.metric(
            "Document Type",
            result.get("document_type", "Unknown")
        )

    with col2:

        st.metric(
            "Confidence",
            f"{result.get('confidence', 0):.2f}%"
        )

    # ----------------------------------------------------
    # ATS Score
    # ----------------------------------------------------

    ats = result.get("ats")

    if ats:

        st.markdown("---")

        st.subheader("🤖 ATS Resume Score")

        st.metric(
            "Overall Score",
            ats.get("overall_score", 0)
        )

        st.write("### Score Breakdown")

        st.json(
            ats.get("breakdown", {})
        )

        st.write("### Recommendations")

        recommendations = ats.get(
            "recommendations",
            []
        )

        if recommendations:

            for recommendation in recommendations:

                st.write(f"• {recommendation}")

        else:

            st.success("Excellent Resume!")

    # ----------------------------------------------------
    # JD Match
    # ----------------------------------------------------

    jd = result.get("jd_match")

    if jd:

        st.markdown("---")

        st.subheader("🎯 Job Description Match")

        st.metric(
            "Match Score",
            f"{jd.get('match_score',0)}%"
        )

        col1, col2 = st.columns(2)

        with col1:

            st.write("### ✅ Matched Skills")

            matched = jd.get(
                "matched_skills",
                []
            )

            if matched:

                for skill in matched:

                    st.success(skill)

            else:

                st.info("No matched skills.")

        with col2:

            st.write("### ❌ Missing Skills")

            missing = jd.get(
                "missing_skills",
                []
            )

            if missing:

                for skill in missing:

                    st.error(skill)

            else:

                st.success("No missing skills!")

    # ----------------------------------------------------
    # Skill Gap
    # ----------------------------------------------------

    gap = result.get("skill_gap")

    if gap:

        st.markdown("---")

        st.subheader("📈 Skill Gap Analysis")

        priority = gap.get(
            "learning_priority",
            []
        )

        if priority:

            for item in priority:

                st.warning(
                    f"{item['skill']} ({item['priority']})"
                )

        recommendation = gap.get(
            "career_recommendation"
        )

        if recommendation:

            st.info(recommendation)

    # ----------------------------------------------------
    # Extracted JSON
    # ----------------------------------------------------

    st.markdown("---")

    st.subheader("📦 Extracted JSON")

    st.json(result)

    # ----------------------------------------------------
    # Download JSON
    # ----------------------------------------------------

    st.download_button(
        "⬇ Download JSON",
        json.dumps(result, indent=4),
        file_name="resume_result.json",
        mime="application/json"
    )