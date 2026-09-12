import json

import pandas as pd
import streamlit as st

from src.database.crud import DocumentCRUD

st.error("🔥 NEW ANALYTICS FILE IS RUNNING")
# ============================================================
# Helpers
# ============================================================

def _to_number(value):
    if value is None:
        return None

    if isinstance(value, (int, float)):
        return float(value)

    try:
        return float(
            str(value)
            .strip()
            .replace("%", "")
        )
    except (TypeError, ValueError):
        return None


def _get_record_value(record, key, default=None):
    """
    Works with both SQLAlchemy objects and dictionaries.
    """

    if isinstance(record, dict):
        return record.get(key, default)

    return getattr(record, key, default)


def _load_json(record):
    raw = _get_record_value(
        record,
        "json_data",
        "{}"
    )

    if isinstance(raw, dict):
        return raw

    try:
        return json.loads(raw or "{}")
    except (
        TypeError,
        json.JSONDecodeError
    ):
        return {}


def _find_value(data, keys):
    """
    Search for a metric in multiple possible locations.
    """

    if not isinstance(data, dict):
        return None

    # Top level
    for key in keys:
        value = data.get(key)

        if value is not None:
            return value

    # analysis
    analysis = data.get("analysis")

    if isinstance(analysis, dict):

        for key in keys:
            value = analysis.get(key)

            if value is not None:
                return value

    # statistics
    statistics = data.get("statistics")

    if isinstance(statistics, dict):

        for key in keys:
            value = statistics.get(key)

            if value is not None:
                return value

    return None


def _get_needs_review(data):
    value = _find_value(
        data,
        [
            "needs_review",
            "human_review",
            "requires_review",
        ]
    )

    if isinstance(value, str):

        return value.strip().lower() in (
            "true",
            "yes",
            "1",
        )

    return bool(value)


# ============================================================
# Convert Database Records → Analytics DataFrame
# ============================================================

def _normalize_records(records):

    rows = []

    for record in records or []:

        data = _load_json(record)

        # ----------------------------------------------------
        # Document Type
        # ----------------------------------------------------

        document_type = (
            _get_record_value(
                record,
                "document_type"
            )
            or data.get("document_type")
            or data.get("type")
            or "unknown"
        )

        # ----------------------------------------------------
        # Confidence
        #
        # Prefer database column.
        # ----------------------------------------------------

        confidence = _get_record_value(
            record,
            "confidence"
        )

        if confidence is None:

            confidence = _find_value(
                data,
                [
                    "confidence",
                    "ocr_score",
                    "extraction_confidence",
                ]
            )

        # ----------------------------------------------------
        # Completion
        # ----------------------------------------------------

        completion = _find_value(
            data,
            [
                "completion",
                "completion_score",
                "completion_rate",
                "completion_percentage",
            ]
        )

        # ----------------------------------------------------
        # Validation
        # ----------------------------------------------------

        validation = _find_value(
            data,
            [
                "validation",
                "validation_score",
                "validation_rate",
            ]
        )

        # ----------------------------------------------------
        # Human Review
        # ----------------------------------------------------

        needs_review = _get_needs_review(data)

        # ----------------------------------------------------
        # File name
        # ----------------------------------------------------

        file_name = _get_record_value(
            record,
            "file_name",
            "Unknown"
        )

        # ----------------------------------------------------
        # Database ID
        # ----------------------------------------------------

        record_id = _get_record_value(
            record,
            "id",
            None
        )

        rows.append(
            {
                "ID": record_id,
                "File Name": file_name,
                "Document Type": str(
                    document_type
                ).strip().title(),

                "Confidence": _to_number(
                    confidence
                ),

                "Completion": _to_number(
                    completion
                ),

                "Validation": _to_number(
                    validation
                ),

                "Needs Review": needs_review,
            }
        )

    return pd.DataFrame(rows)


# ============================================================
# Main Analytics Dashboard
# ============================================================

def render_analytics(records=None):

    st.header("📊 Analytics Dashboard")

    st.caption(
        "Live performance analytics from the IDP database"
    )

    # ========================================================
    # Load database records
    # ========================================================

    crud = None

    try:

        if records is None:

            crud = DocumentCRUD()

            records = crud.get_all()

        # ----------------------------------------------------
        # Debug information
        # ----------------------------------------------------

        record_count = len(records or [])

        st.caption(
            f"🗄 Database records loaded: {record_count}"
        )

        # ----------------------------------------------------
        # Normalize
        # ----------------------------------------------------

        df = _normalize_records(records)

    except Exception as exc:

        st.error(
            "❌ Could not load analytics data from database."
        )

        with st.expander("Technical Error"):
            st.exception(exc)

        return

    finally:

        if crud is not None:
            crud.close()

    # ========================================================
    # Empty database
    # ========================================================

    if df.empty:

        st.warning(
            "No processing records were found in the database."
        )

        st.info(
            "Process a Resume, Invoice, Receipt, or Form first."
        )

        return

    # ========================================================
    # KPI calculations
    # ========================================================

    avg_confidence = (
        df["Confidence"]
        .dropna()
        .mean()
    )

    avg_completion = (
        df["Completion"]
        .dropna()
        .mean()
    )

    avg_validation = (
        df["Validation"]
        .dropna()
        .mean()
    )

    review_count = int(
        df["Needs Review"].sum()
    )

    # ========================================================
    # KPI CARDS
    # ========================================================

    st.subheader("📌 System KPIs")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "📄 Documents Processed",
        len(df)
    )

    c2.metric(
        "🎯 Avg Confidence",
        (
            f"{avg_confidence:.1f}%"
            if pd.notna(avg_confidence)
            else "N/A"
        )
    )

    c3.metric(
        "✅ Avg Validation",
        (
            f"{avg_validation:.1f}%"
            if pd.notna(avg_validation)
            else "N/A"
        )
    )

    c4.metric(
        "⚠️ Needs Review",
        review_count
    )

    st.divider()

    # ========================================================
    # GRAPH 1
    # Documents by Type
    # ========================================================

    st.subheader(
        "📄 Documents Processed by Type"
    )

    type_counts = (
        df["Document Type"]
        .value_counts()
        .rename("Documents")
        .to_frame()
    )

    st.bar_chart(
        type_counts,
        use_container_width=True
    )

    st.divider()

    # ========================================================
    # GRAPH 2
    # Quality by Type
    # ========================================================

    st.subheader(
        "🎯 Quality Metrics by Document Type"
    )

    quality = (
        df.groupby(
            "Document Type"
        )[
            [
                "Confidence",
                "Completion",
                "Validation",
            ]
        ]
        .mean()
        .round(1)
    )

    if not quality.empty:

        st.bar_chart(
            quality,
            use_container_width=True
        )

    else:

        st.info(
            "Quality metrics are not available."
        )

    st.divider()

    # ========================================================
    # GRAPH 3
    # Human Review
    # ========================================================

    st.subheader(
        "⚠️ Human Review by Document Type"
    )

    review = (
        df.groupby(
            "Document Type"
        )["Needs Review"]
        .sum()
        .astype(int)
        .rename(
            "Documents Requiring Review"
        )
        .to_frame()
    )

    st.bar_chart(
        review,
        use_container_width=True
    )

    st.divider()

    # ========================================================
    # GRAPH 4
    # Overall Quality
    # ========================================================

    st.subheader(
        "📊 Overall Processing Quality"
    )

    overall = pd.DataFrame(
        {
            "Score": [
                (
                    avg_confidence
                    if pd.notna(avg_confidence)
                    else 0
                ),
                (
                    avg_completion
                    if pd.notna(avg_completion)
                    else 0
                ),
                (
                    avg_validation
                    if pd.notna(avg_validation)
                    else 0
                ),
            ]
        },
        index=[
            "Confidence",
            "Completion",
            "Validation",
        ]
    )

    st.bar_chart(
        overall,
        use_container_width=True
    )

    st.divider()

    # ========================================================
    # DOCUMENT TYPE PERFORMANCE
    # ========================================================

    st.subheader(
        "📋 Document-Type Performance"
    )

    performance = (
        df.groupby(
            "Document Type"
        )
        .agg(
            Documents=(
                "Document Type",
                "size"
            ),

            Avg_Confidence=(
                "Confidence",
                "mean"
            ),

            Avg_Completion=(
                "Completion",
                "mean"
            ),

            Avg_Validation=(
                "Validation",
                "mean"
            ),

            Needs_Review=(
                "Needs Review",
                "sum"
            ),
        )
        .reset_index()
    )

    performance[
        "Avg_Confidence"
    ] = performance[
        "Avg_Confidence"
    ].round(1)

    performance[
        "Avg_Completion"
    ] = performance[
        "Avg_Completion"
    ].round(1)

    performance[
        "Avg_Validation"
    ] = performance[
        "Avg_Validation"
    ].round(1)

    st.dataframe(
        performance,
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    # ========================================================
    # DATABASE RECORDS
    # ========================================================

    st.subheader(
        "🗄 Database Processing History"
    )

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )