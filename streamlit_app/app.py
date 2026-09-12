import sys
import tempfile
from pathlib import Path

from dotenv import load_dotenv

# --------------------------------------------------
# Add Project Root
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Load project environment variables
load_dotenv(PROJECT_ROOT / ".env")

# --------------------------------------------------
# Streamlit
# --------------------------------------------------

import streamlit as st

from components.sidebar import render_sidebar
from services.database import get_dashboard_stats


# Pages
from streamlit_app.resume import show as resume_page

from src.database.database import Base, engine
from src.database.models import Document
from src.database.crud import DocumentCRUD
import json

Base.metadata.create_all(bind=engine)

# Document pipeline
from src.pipelines.smart_document_pipeline import SmartDocumentPipeline

# Receipt extraction
from src.extraction.receipt_extractor import ReceiptExtractor


# --------------------------------------------------
# Page Config
# --------------------------------------------------

st.set_page_config(
    page_title="Intelligent Document Processing",
    page_icon="📄",
    layout="wide",
)

# ==================================================
# Professional Dark UI (presentation only)
# ==================================================
st.markdown("""
<style>
:root {
    --bg: #0b1120;
    --panel: #111827;
    --panel2: #162033;
    --border: #263449;
    --text: #f8fafc;
    --muted: #a7b3c7;
    --accent: #60a5fa;
}

/* Main application */
.stApp,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
.main,
.main .block-container {
    background: var(--bg) !important;
    color: var(--text) !important;
}

.main .block-container {
    max-width: 1500px !important;
    padding-top: 1.25rem !important;
    padding-bottom: 3rem !important;
}

/* Text visibility everywhere in main content */
.main h1, .main h2, .main h3, .main h4, .main h5, .main h6,
.main p, .main li, .main label,
.main [data-testid="stMarkdownContainer"],
.main [data-testid="stMarkdownContainer"] *,
.main [data-testid="stCaptionContainer"],
.main [data-testid="stCaptionContainer"] * {
    color: var(--text) !important;
}

.main [data-testid="stCaptionContainer"],
.main [data-testid="stCaptionContainer"] * {
    color: var(--muted) !important;
}

/* Sidebar stays dark */
section[data-testid="stSidebar"] {
    background: #080f1e !important;
    border-right: 1px solid #1d2a3d !important;
}
section[data-testid="stSidebar"] * {
    color: #e5edf8 !important;
}

/* Metrics */
div[data-testid="stMetric"] {
    background: var(--panel) !important;
    border: 1px solid var(--border) !important;
    border-radius: 14px !important;
    padding: 15px 16px !important;
    box-shadow: 0 8px 24px rgba(0,0,0,.18) !important;
}
div[data-testid="stMetric"] * {
    color: #f8fafc !important;
}
div[data-testid="stMetricLabel"],
div[data-testid="stMetricLabel"] * {
    color: #a7b3c7 !important;
}
div[data-testid="stMetricValue"],
div[data-testid="stMetricValue"] * {
    color: #ffffff !important;
    font-weight: 750 !important;
}
div[data-testid="stMetricDelta"],
div[data-testid="stMetricDelta"] * {
    color: #86efac !important;
}

/* Buttons */
.stButton > button {
    background: #17243a !important;
    color: #f8fafc !important;
    border: 1px solid #334155 !important;
    border-radius: 10px !important;
    min-height: 42px !important;
    font-weight: 650 !important;
}
.stButton > button:hover {
    background: #20304a !important;
    color: #ffffff !important;
    border-color: #4b6385 !important;
}

/* Uploaders */
section[data-testid="stFileUploaderDropzone"] {
    background: #111827 !important;
    border: 1.5px dashed #3b4b63 !important;
    border-radius: 14px !important;
}
section[data-testid="stFileUploaderDropzone"] * {
    color: #dbe7f5 !important;
}
section[data-testid="stFileUploaderDropzone"] button {
    background: #1b2940 !important;
    color: #ffffff !important;
    border: 1px solid #40526d !important;
}

/* Inputs and textareas */
.main input, .main textarea {
    background: #111827 !important;
    color: #f8fafc !important;
    border-color: #334155 !important;
    caret-color: #ffffff !important;
}
.main input::placeholder, .main textarea::placeholder {
    color: #7f8da3 !important;
}

/* Selects / BaseWeb */
.main [data-baseweb="select"] > div {
    background: #111827 !important;
    border-color: #334155 !important;
}
.main [data-baseweb="select"] * {
    color: #f8fafc !important;
}
[data-baseweb="popover"],
[role="listbox"], [role="option"] {
    background: #111827 !important;
    color: #f8fafc !important;
}
[role="option"]:hover {
    background: #1e293b !important;
}

/* Dataframes */
div[data-testid="stDataFrame"] {
    background: #111827 !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    overflow: hidden !important;
}

/* Expanders */
div[data-testid="stExpander"] {
    background: #111827 !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
}
div[data-testid="stExpander"] summary,
div[data-testid="stExpander"] summary * {
    color: #f8fafc !important;
}

/* Code / JSON */
.main pre, .main code {
    background: #080f1e !important;
    color: #dbeafe !important;
}

/* Tabs */
.main button[data-baseweb="tab"] {
    color: #9fb0c5 !important;
}
.main button[data-baseweb="tab"][aria-selected="true"] {
    color: #ffffff !important;
}

/* Alerts and dividers */
div[data-testid="stAlert"] { border-radius: 10px !important; }
hr { border-color: #263449 !important; }

/* Professional dashboard cards */
.idp-hero {
    padding: 28px 30px;
    border-radius: 18px;
    background: linear-gradient(135deg, #111c31 0%, #18263d 100%);
    border: 1px solid #293952;
    margin-bottom: 24px;
    box-shadow: 0 18px 40px rgba(0,0,0,.24);
}
.idp-hero h1 { color: #ffffff !important; margin: 0 0 6px 0; }
.idp-hero p { color: #b9c7da !important; margin: 0; }
.idp-badge {
    display: inline-block;
    margin-top: 15px;
    padding: 6px 12px;
    border-radius: 999px;
    background: rgba(34,197,94,.12);
    color: #86efac !important;
    border: 1px solid rgba(74,222,128,.28);
    font-weight: 700;
}
.idp-section { margin: 26px 0 12px 0; }
.idp-section h3 { color: #f8fafc !important; margin: 0; }
.idp-card {
    background: #111827;
    border: 1px solid #263449;
    border-radius: 14px;
    padding: 18px;
    box-shadow: 0 8px 24px rgba(0,0,0,.18);
    min-height: 95px;
}
.idp-card-title { color: #8fa0b8 !important; font-size: .78rem; font-weight: 700; text-transform: uppercase; letter-spacing: .07em; }
.idp-card-value { color: #ffffff !important; font-size: 1.42rem; font-weight: 750; margin-top: 5px; }
.idp-card-sub { color: #9fb0c5 !important; font-size: .82rem; margin-top: 4px; }
.pipeline { display: flex; gap: 8px; align-items: center; flex-wrap: wrap; margin-top: 8px; }
.pipeline-step { background: #111827; border: 1px solid #304057; border-radius: 10px; padding: 10px 13px; color: #e5edf8 !important; font-size: .85rem; font-weight: 650; }
.pipeline-arrow { color: #71839d !important; font-weight: 800; }
.idp-footer { text-align: center; color: #71839d !important; font-size: .8rem; margin-top: 35px; padding-top: 15px; border-top: 1px solid #263449; }

/* Static app title */
.idp-top-title { color: #f8fafc !important; font-size: 1.7rem; font-weight: 750; }
.idp-top-subtitle { color: #9fb0c5 !important; font-size: .9rem; }
</style>
""", unsafe_allow_html=True)


def save_document_result(result, file_name):
    """
    Save processed document result into SQLite database.
    """

    crud = DocumentCRUD()

    try:
        document_type = str(
            result.get("document_type", "unknown")
        ).strip().lower()

        # Try to get confidence from different possible locations
        confidence = result.get("confidence")

        if confidence is None:
            stats = result.get("statistics") or {}

            if isinstance(stats, dict):
                confidence = stats.get("confidence")

        try:
            confidence = float(confidence or 0.0)
        except (TypeError, ValueError):
            confidence = 0.0

        # Make JSON serializable
        safe_result = json.loads(
            json.dumps(result, default=str)
        )

        raw_text = (
            result.get("ocr_text")
            or result.get("raw_text")
            or ""
        )

        document = crud.create(
            file_name=file_name,
            document_type=document_type,
            confidence=confidence,
            raw_text=raw_text,
            json_data=safe_result,
        )

        return document

    finally:
        crud.close()
# --------------------------------------------------
# Sidebar
# --------------------------------------------------

page = render_sidebar()


# --------------------------------------------------
# Title
# --------------------------------------------------

st.title("📄 Intelligent Document Processing System")
st.markdown("---")


# ==================================================
# Dashboard
# ==================================================

if page == "🏠 Dashboard":

    stats = get_dashboard_stats()
    records = stats.get("records", [])

    total = stats.get("total", 0)
    resume_count = stats.get("resume", 0)
    invoice_count = stats.get("invoice", 0)
    receipt_count = stats.get("receipt", 0)
    form_count = stats.get("form", 0)

    confidences = [
        float(r.confidence)
        for r in records
        if getattr(r, "confidence", None) is not None
    ]
    avg_confidence = sum(confidences) / len(confidences) if confidences else 0

    review_count = 0
    for r in records:
        try:
            payload = json.loads(r.json_data or "{}")
            if payload.get("needs_review") is True:
                review_count += 1
        except Exception:
            pass

    st.markdown("""
    <div class="idp-hero">
        <h1>Intelligent Document Processing</h1>
        <p>AI-powered document understanding, extraction, validation and analytics.</p>
        <span class="idp-badge">● SYSTEM ONLINE</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="idp-section"><h3>Executive Overview</h3></div>', unsafe_allow_html=True)

    k1, k2, k3, k4, k5, k6 = st.columns(6)
    k1.metric("Total Documents", total)
    k2.metric("Resumes", resume_count)
    k3.metric("Invoices", invoice_count)
    k4.metric("Receipts", receipt_count)
    k5.metric("Forms", form_count)
    k6.metric("Avg. Confidence", f"{avg_confidence:.1f}%")

    st.markdown('<div class="idp-section"><h3>AI Processing Pipeline</h3></div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="pipeline">
        <div class="pipeline-step">1. Upload</div><div class="pipeline-arrow">→</div>
        <div class="pipeline-step">2. OCR</div><div class="pipeline-arrow">→</div>
        <div class="pipeline-step">3. Classification</div><div class="pipeline-arrow">→</div>
        <div class="pipeline-step">4. Extraction</div><div class="pipeline-arrow">→</div>
        <div class="pipeline-step">5. Validation</div><div class="pipeline-arrow">→</div>
        <div class="pipeline-step">6. Database</div><div class="pipeline-arrow">→</div>
        <div class="pipeline-step">7. Analytics</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="idp-section"><h3>System Health</h3></div>', unsafe_allow_html=True)
    h1, h2, h3, h4 = st.columns(4)
    with h1:
        st.markdown('<div class="idp-card"><div class="idp-card-title">OCR Engine</div><div class="idp-card-value">Operational</div><div class="idp-card-sub">EasyOCR pipeline ready</div></div>', unsafe_allow_html=True)
    with h2:
        st.markdown('<div class="idp-card"><div class="idp-card-title">Classifier</div><div class="idp-card-value">Ready</div><div class="idp-card-sub">Document routing active</div></div>', unsafe_allow_html=True)
    with h3:
        st.markdown('<div class="idp-card"><div class="idp-card-title">Database</div><div class="idp-card-value">Connected</div><div class="idp-card-sub">SQLite persistence active</div></div>', unsafe_allow_html=True)
    with h4:
        st.markdown(f'<div class="idp-card"><div class="idp-card-title">Review Queue</div><div class="idp-card-value">{review_count}</div><div class="idp-card-sub">Documents flagged for review</div></div>', unsafe_allow_html=True)

    st.markdown('<div class="idp-section"><h3>AI Capabilities</h3></div>', unsafe_allow_html=True)
    a1, a2, a3 = st.columns(3)
    with a1:
        st.markdown('<div class="idp-card"><div class="idp-card-title">Resume Intelligence</div><div class="idp-card-value">ATS Scoring</div><div class="idp-card-sub">Resume ↔ Job Description matching and skill-gap analysis.</div></div>', unsafe_allow_html=True)
    with a2:
        st.markdown('<div class="idp-card"><div class="idp-card-title">Document Intelligence</div><div class="idp-card-value">Smart Extraction</div><div class="idp-card-sub">Invoice, receipt and form information extracted from documents.</div></div>', unsafe_allow_html=True)
    with a3:
        st.markdown('<div class="idp-card"><div class="idp-card-title">Data Operations</div><div class="idp-card-value">Traceable Records</div><div class="idp-card-sub">Processed documents, OCR text and structured JSON stored in the database.</div></div>', unsafe_allow_html=True)

    st.markdown('<div class="idp-section"><h3>Recent Documents</h3></div>', unsafe_allow_html=True)
    if records:
        recent_data = []
        for r in records[:8]:
            recent_data.append({
                "ID": r.id,
                "File": r.file_name,
                "Type": str(r.document_type).title(),
                "Confidence": f"{r.confidence:.2f}%" if r.confidence is not None else "N/A",
            })
        st.dataframe(recent_data, use_container_width=True, hide_index=True)
    else:
        st.info("No processed documents yet. Use the sidebar to process your first document.")

    st.markdown("""
    <div class="idp-footer">
        Intelligent Document Processing System · OCR · AI Extraction · Validation · Analytics
    </div>
    """, unsafe_allow_html=True)


# ==================================================
# Resume
# ==================================================

elif page == "📄 Resume":
    resume_page()


# ==================================================
# Invoice
# ==================================================

elif page == "🧾 Invoice":

    st.header("🧾 Invoice Analysis")
    st.caption(
        "Upload an invoice image or PDF. OCR, classification and "
        "extraction are automatic."
    )

    uploaded_file = st.file_uploader(
        "Upload Invoice",
        type=["png", "jpg", "jpeg", "bmp", "tif", "tiff", "pdf"],
        key="invoice_upload",
    )

    if uploaded_file is not None:

        suffix = Path(uploaded_file.name).suffix.lower()
        st.write(f"**File:** {uploaded_file.name}")

        if st.button(
            "🔎 Analyze Invoice",
            type="primary",
            use_container_width=True,
        ):

            temp_path = None
            progress = st.progress(
                0,
                text="Preparing document...",
            )

            try:

                with tempfile.NamedTemporaryFile(
                    delete=False,
                    suffix=suffix,
                ) as temp_file:
                    temp_file.write(uploaded_file.getbuffer())
                    temp_path = Path(temp_file.name)

                progress.progress(20, text="Running OCR...")

                pipeline = SmartDocumentPipeline()

                progress.progress(
                    55,
                    text="Classifying and extracting...",
                )

                result = pipeline.process(str(temp_path))

                detected_type = str(
                    result.get("document_type", "")
                ).strip().lower()

                if detected_type != "invoice":
                    raise ValueError(
                        f"Document detected as "
                        f"'{detected_type or 'unknown'}', not invoice. "
                        "Please upload a clearer invoice image/PDF."
                    )

                progress.progress(
                    100,
                    text="Invoice analysis completed.",
                )

                save_document_result(
                     result,
                     uploaded_file.name
                )

                st.session_state["invoice_result"] = result

                st.success(
                   "Invoice processed successfully and saved to database."
                )

            except Exception as exc:

                progress.empty()
                st.error("Invoice processing failed.")

                with st.expander("Technical Error"):
                    st.exception(exc)

            finally:

                if temp_path is not None:
                    try:
                        temp_path.unlink(missing_ok=True)
                    except Exception:
                        pass

        result = st.session_state.get("invoice_result")

        if result:

            st.markdown("---")
            st.subheader("Extracted Invoice Information")

            c1, c2, c3, c4 = st.columns(4)

            c1.metric(
                "Invoice Number",
                result.get("invoice_number") or "Not detected",
            )

            c2.metric(
                "Invoice Date",
                result.get("invoice_date") or "Not detected",
            )

            c3.metric(
                "Subtotal",
                result.get("subtotal") or "Not detected",
            )

            c4.metric(
                "Total",
                result.get("total") or "Not detected",
            )

            st.markdown("### Vendor")

            vendor = result.get("vendor") or {}

            st.write(
                f"**Name:** {vendor.get('name') or 'Not detected'}"
            )

            st.write(
                f"**Address:** {vendor.get('address') or 'Not detected'}"
            )

            st.write(
                f"**Phone:** {vendor.get('phone') or 'Not detected'}"
            )

            st.write(
                f"**Email:** {vendor.get('email') or 'Not detected'}"
            )

            st.markdown("### Customer")

            customer = result.get("customer") or {}

            st.write(
                f"**Name:** {customer.get('name') or 'Not detected'}"
            )

            st.markdown("### Financial Information")

            f1, f2, f3, f4, f5 = st.columns(5)

            f1.metric(
                "Currency",
                result.get("currency") or "Not detected",
            )

            f2.metric(
                "Subtotal",
                result.get("subtotal") or "Not detected",
            )

            f3.metric(
                "Tax",
                result.get("tax") or "Not detected",
            )

            f4.metric(
                "Discount",
                result.get("discount") or "Not detected",
            )

            f5.metric(
                "Total",
                result.get("total") or "Not detected",
            )

            st.markdown("### Payment")

            st.write(
                result.get("payment_method")
                or "Payment method not detected."
            )

            st.markdown("### Invoice Items")

            items = result.get("items") or []

            if items:
                st.json(items, expanded=True)
            else:
                st.info(
                    "No invoice line items were confidently detected."
                )

            stats = result.get("statistics") or {}

            st.markdown("### Extraction Statistics")

            s1, s2, s3, s4 = st.columns(4)

            s1.metric(
                "OCR Lines",
                stats.get("line_count", 0),
            )

            s2.metric(
                "Items",
                stats.get("item_count", len(items)),
            )

            s3.metric(
                "Vendor Found",
                "Yes" if stats.get("vendor_found") else "No",
            )

            s4.metric(
                "Customer Found",
                "Yes" if stats.get("customer_found") else "No",
            )

            with st.expander("View Raw OCR Text"):
                st.text(
                    result.get("ocr_text")
                    or result.get("raw_text")
                    or ""
                )

            with st.expander("View Complete JSON"):
                st.json(result)


# ==================================================
# Receipt
# ==================================================

elif page == "🧾 Receipt":

    st.header("🧾 Receipt Analysis")

    st.caption(
        "Upload a receipt image or PDF. OCR and generic receipt extraction "
        "are performed automatically."
    )

    uploaded_file = st.file_uploader(
        "Upload Receipt",
        type=["png", "jpg", "jpeg", "bmp", "tif", "tiff", "pdf"],
        key="receipt_upload",
    )

    if uploaded_file is not None:

        suffix = Path(uploaded_file.name).suffix.lower()
        st.write(f"**File:** {uploaded_file.name}")

        if st.button(
            "🔎 Analyze Receipt",
            type="primary",
            use_container_width=True,
        ):

            temp_path = None

            progress = st.progress(
                0,
                text="Preparing document...",
            )

            try:

                # ------------------------------------------
                # Save uploaded file temporarily
                # ------------------------------------------

                with tempfile.NamedTemporaryFile(
                    delete=False,
                    suffix=suffix,
                ) as temp_file:

                    temp_file.write(
                        uploaded_file.getbuffer()
                    )

                    temp_path = Path(temp_file.name)

                # ------------------------------------------
                # OCR + Receipt Extraction
                # ------------------------------------------

                progress.progress(
                    30,
                    text="Running OCR...",
                )

                from src.ocr.easy_ocr import OCRExtractor

                ocr = OCRExtractor()

                ocr_results = ocr.extract(
                    str(temp_path)
                )

                # ------------------------------------------
                # Normalize OCR output safely
                #
                # OCRExtractor versions may return:
                #   - string
                #   - dict
                #   - list[str]
                #   - list[dict]
                #   - other OCR objects
                #
                # Never call .get() on an object until
                # its type has been checked.
                # ------------------------------------------

                ocr_lines = []

                if isinstance(ocr_results, str):

                    ocr_lines = [
                        line.strip()
                        for line in ocr_results.splitlines()
                        if line and line.strip()
                    ]

                elif isinstance(ocr_results, dict):

                    text_value = ocr_results.get("text", "")

                    if isinstance(text_value, str):

                        ocr_lines = [
                            line.strip()
                            for line in text_value.splitlines()
                            if line and line.strip()
                        ]

                    elif isinstance(text_value, (list, tuple)):

                        for line in text_value:

                            if isinstance(line, str):
                                text = line.strip()

                            elif isinstance(line, dict):
                                text = str(
                                    line.get("text", "")
                                ).strip()

                            else:
                                text = str(line).strip()

                            if text:
                                ocr_lines.append(text)

                elif isinstance(ocr_results, (list, tuple)):

                    for item in ocr_results:

                        if isinstance(item, str):

                            text = item.strip()

                        elif isinstance(item, dict):

                            text = str(
                                item.get("text", "")
                            ).strip()

                        elif isinstance(item, (list, tuple)):

                            # Some OCR libraries return:
                            # [bbox, text, confidence]
                            # or similar tuple/list structures.
                            text = ""

                            for part in item:

                                if isinstance(part, str):
                                    candidate = part.strip()

                                    if candidate:
                                        text = candidate
                                        break

                            if not text:
                                text = str(item).strip()

                        else:

                            text = str(item).strip()

                        if text:
                            ocr_lines.append(text)

                else:

                    text = str(ocr_results).strip()

                    if text:
                        ocr_lines = [
                            line.strip()
                            for line in text.splitlines()
                            if line and line.strip()
                        ]

                # Final cleanup
                ocr_lines = [
                    line.strip()
                    for line in ocr_lines
                    if isinstance(line, str) and line.strip()
                ]

                ocr_text = "\n".join(ocr_lines)

                if not ocr_text.strip():
                    raise ValueError(
                        "No readable text was detected from the receipt."
                    )

                progress.progress(
                    70,
                    text="Extracting receipt information...",
                )

                # ------------------------------------------
                # Generic Receipt Extraction
                # ------------------------------------------

                receipt_extractor = ReceiptExtractor()

                result = receipt_extractor.extract(
                    ocr_text
                )

                # ------------------------------------------
                # Metadata
                # ------------------------------------------

                result["document_type"] = "receipt"
                result["file_name"] = uploaded_file.name
                result["input_type"] = suffix
                result["page_count"] = 1
                result["ocr_text"] = ocr_text

                # ------------------------------------------
                # Save result
                # ------------------------------------------

                save_document_result(
                    result,
                    uploaded_file.name
                )

                st.session_state["receipt_result"] = result

                progress.progress(
                   100,
                   text="Receipt analysis completed.",
                )

                st.success(
                   "Receipt processed successfully and saved to database."
                )

            except Exception as exc:

                progress.empty()

                st.error(
                    "Receipt processing failed."
                )

                with st.expander("Technical Error"):
                    st.exception(exc)

            finally:

                if temp_path is not None:

                    try:
                        temp_path.unlink(
                            missing_ok=True
                        )
                    except Exception:
                        pass

        # ==================================================
        # Display Result
        # ==================================================

        result = st.session_state.get(
            "receipt_result"
        )

        if result:

            st.markdown("---")

            st.subheader(
                "Extracted Receipt Information"
            )

            # ------------------------------------------
            # Basic Information
            # ------------------------------------------

            c1, c2, c3, c4 = st.columns(4)

            c1.metric(
                "Receipt Number",
                result.get("receipt_number")
                or "Not detected",
            )

            c2.metric(
                "Receipt Date",
                result.get("receipt_date")
                or "Not detected",
            )

            c3.metric(
                "Subtotal",
                result.get("subtotal")
                or "Not detected",
            )

            c4.metric(
                "Total",
                result.get("total")
                or "Not detected",
            )

            # ------------------------------------------
            # Merchant
            # ------------------------------------------

            st.markdown("### Merchant")

            merchant = result.get("merchant") or {}

            # Defensive protection if extractor returns
            # an unexpected non-dictionary value.
            if not isinstance(merchant, dict):
                merchant = {}

            st.write(
                f"**Name:** "
                f"{merchant.get('name') or 'Not detected'}"
            )

            st.write(
                f"**Address:** "
                f"{merchant.get('address') or 'Not detected'}"
            )

            st.write(
                f"**Phone:** "
                f"{merchant.get('phone') or 'Not detected'}"
            )

            st.write(
                f"**Email:** "
                f"{merchant.get('email') or 'Not detected'}"
            )

            # ------------------------------------------
            # Financial Information
            # ------------------------------------------

            st.markdown(
                "### Financial Information"
            )

            f1, f2, f3, f4, f5 = st.columns(5)

            f1.metric(
                "Currency",
                result.get("currency")
                or "Not detected",
            )

            f2.metric(
                "Subtotal",
                result.get("subtotal")
                or "Not detected",
            )

            f3.metric(
                "Tax",
                result.get("tax")
                or "Not detected",
            )

            f4.metric(
                "Discount",
                result.get("discount")
                or "Not detected",
            )

            f5.metric(
                "Total",
                result.get("total")
                or "Not detected",
            )

            # ------------------------------------------
            # Payment
            # ------------------------------------------

            st.markdown("### Payment")

            st.write(
                result.get("payment_method")
                or "Payment method not detected."
            )

            # ------------------------------------------
            # Items
            # ------------------------------------------

            st.markdown("### Receipt Items")

            items = result.get("items") or []

            if not isinstance(items, list):
                items = []

            if items:

                st.json(
                    items,
                    expanded=True,
                )

            else:

                st.info(
                    "No receipt line items were "
                    "confidently detected."
                )

            # ------------------------------------------
            # Statistics
            # ------------------------------------------

            stats = result.get("statistics") or {}

            if not isinstance(stats, dict):
                stats = {}

            st.markdown(
                "### Extraction Statistics"
            )

            s1, s2, s3, s4 = st.columns(4)

            # Safe OCR text for the results page.
            # `ocr_text` is created during processing, but may not exist
            # after Streamlit reruns when the result comes from session state.
            ocr_text_value = (
                result.get("ocr_text")
                or result.get("raw_text")
                or ""
            )

            s1.metric(
                "OCR Lines",
                stats.get(
                    "line_count",
                    len(ocr_text_value.splitlines()),
                ),
            )

            s2.metric(
                "Items",
                stats.get(
                    "item_count",
                    len(items),
                ),
            )

            s3.metric(
                "Merchant Found",
                "Yes"
                if stats.get("merchant_found")
                else "No",
            )

            s4.metric(
                "Receipt Number Found",
                "Yes"
                if stats.get("receipt_number_found")
                else "No",
            )

            # ------------------------------------------
            # Raw OCR
            # ------------------------------------------

            with st.expander(
                "View Raw OCR Text"
            ):

                st.text(
                    result.get(
                        "ocr_text",
                        "",
                    )
                )

            # ------------------------------------------
            # Complete JSON
            # ------------------------------------------

            with st.expander(
                "View Complete JSON"
            ):

                st.json(result)


# ==================================================
# Form
# ==================================================

elif page == "📋 Form":

    st.header("📋 Form Analysis")

    st.caption(
        "Upload a form image or PDF. OCR, classification and "
        "form-field extraction are performed automatically."
    )

    uploaded_file = st.file_uploader(
        "Upload Form",
        type=["png", "jpg", "jpeg", "bmp", "tif", "tiff", "pdf"],
        key="form_upload",
    )

    if uploaded_file is not None:

        suffix = Path(uploaded_file.name).suffix.lower()
        st.write(f"**File:** {uploaded_file.name}")

        if st.button(
            "🔎 Analyze Form",
            type="primary",
            use_container_width=True,
        ):

            temp_path = None
            progress = st.progress(
                0,
                text="Preparing document...",
            )

            try:

                with tempfile.NamedTemporaryFile(
                    delete=False,
                    suffix=suffix,
                ) as temp_file:
                    temp_file.write(uploaded_file.getbuffer())
                    temp_path = Path(temp_file.name)

                progress.progress(
                    25,
                    text="Running OCR...",
                )

                pipeline = SmartDocumentPipeline()

                progress.progress(
                    60,
                    text="Classifying and extracting form fields...",
                )

                result = pipeline.process(str(temp_path))

                detected_type = str(
                    result.get("document_type", "")
                ).strip().lower()

                if detected_type != "form":
                    raise ValueError(
                        f"Document detected as "
                        f"'{detected_type or 'unknown'}', not form. "
                        "Please upload a form document."
                    )

                result["file_name"] = uploaded_file.name
                result["input_type"] = suffix
                result["page_count"] = result.get("page_count", 1)
                
                save_document_result(
                    result,
                    uploaded_file.name
                )
               
                st.session_state["form_result"] = result

                progress.progress(
                    100,
                    text="Form analysis completed.",
                )

                st.success(
                    "Form processed successfully and saved to database."
                )

            except Exception as exc:

                progress.empty()

                st.error(
                    "Form processing failed."
                )

                with st.expander("Technical Error"):
                    st.exception(exc)

            finally:

                if temp_path is not None:
                    try:
                        temp_path.unlink(missing_ok=True)
                    except Exception:
                        pass

        # ==================================================
        # Display Form Result
        # ==================================================

        result = st.session_state.get("form_result")

        if result:

            st.markdown("---")
            st.subheader("Extracted Form Information")

            # ------------------------------------------
            # Main form metrics
            # ------------------------------------------

            fields = result.get("fields") or {}

            if not isinstance(fields, dict):
                fields = {}

            missing_fields = result.get("missing_fields") or []

            if not isinstance(missing_fields, list):
                missing_fields = []

            completion = result.get("completion_score")

            if completion is None:
                completion = result.get("completion_percentage")

            validation = result.get("validation_score")

            c1, c2, c3 = st.columns(3)

            c1.metric(
                "Fields Extracted",
                len(fields),
            )

            c2.metric(
                "Completion",
                f"{completion:.2f}%"
                if isinstance(completion, (int, float))
                else "Not available",
            )

            c3.metric(
                "Validation",
                f"{validation:.2f}%"
                if isinstance(validation, (int, float))
                else "Not available",
            )

            # ------------------------------------------
            # Extracted fields
            # ------------------------------------------

            st.markdown("### Extracted Fields")

            if fields:

                for field_name, field_value in fields.items():

                    if isinstance(field_value, dict):
                        value = (
                            field_value.get("value")
                            or field_value.get("text")
                            or ""
                        )
                    else:
                        value = field_value

                    st.write(
                        f"**{str(field_name).replace('_', ' ').title()}:** "
                        f"{value if value not in (None, '') else 'Not detected'}"
                    )

            else:

                # Fallback for extractors that return fields
                # directly at the top level.
                excluded = {
                    "document_type",
                    "missing_fields",
                    "completion_score",
                    "completion_percentage",
                    "validation_score",
                    "raw_text",
                    "ocr_text",
                    "statistics",
                    "file_name",
                    "input_type",
                    "page_count",
                }

                direct_fields = {
                    k: v
                    for k, v in result.items()
                    if k not in excluded
                    and not isinstance(v, (dict, list))
                }

                if direct_fields:

                    for field_name, field_value in direct_fields.items():
                        st.write(
                            f"**{str(field_name).replace('_', ' ').title()}:** "
                            f"{field_value if field_value not in (None, '') else 'Not detected'}"
                        )

                else:
                    st.info(
                        "No structured form fields were confidently detected."
                    )

            # ------------------------------------------
            # Missing fields
            # ------------------------------------------

            if missing_fields:

                st.markdown("### Missing Fields")
                st.warning(", ".join(map(str, missing_fields)))

            # ------------------------------------------
            # Statistics
            # ------------------------------------------

            stats = result.get("statistics") or {}

            if isinstance(stats, dict) and stats:

                st.markdown("### Extraction Statistics")
                st.json(stats, expanded=True)

            # ------------------------------------------
            # Raw OCR
            # ------------------------------------------

            with st.expander("View Raw OCR Text"):

                st.text(
                    result.get("ocr_text")
                    or result.get("raw_text")
                    or ""
                )

            # ------------------------------------------
            # Complete JSON
            # ------------------------------------------

            with st.expander("View Complete JSON"):

                st.json(result)


# ==================================================
# Analytics
# ==================================================

elif page == "📊 Analytics":

    import sys
    from pathlib import Path

    analytics_file = (
        Path(__file__).resolve().parent
        / "analytics_dashboard.py"
    )

    st.write(
        "Analytics file:",
        str(analytics_file)
    )

    if not analytics_file.exists():
        st.error(
            f"Analytics file not found: {analytics_file}"
        )
    else:
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "idp_analytics_dashboard",
            analytics_file
        )

        analytics_module = importlib.util.module_from_spec(
            spec
        )

        spec.loader.exec_module(
            analytics_module
        )

        analytics_module.render_analytics()


# ==================================================
# Database
# ==================================================

# ==================================================
# Database
# ==================================================

elif page == "🗄 Database":

    st.header("🗄 Database")
    st.caption(
        "View and manage processed document records stored in SQLite."
    )

    from src.database.crud import DocumentCRUD

    crud = DocumentCRUD()

    try:

        # ------------------------------------------
        # Load records
        # ------------------------------------------

        records = crud.get_all()

        # ------------------------------------------
        # Database Summary
        # ------------------------------------------

        st.subheader("📊 Database Summary")

        total = len(records)

        resume_count = sum(
            1
            for record in records
            if str(record.document_type).lower() == "resume"
        )

        invoice_count = sum(
            1
            for record in records
            if str(record.document_type).lower() == "invoice"
        )

        receipt_count = sum(
            1
            for record in records
            if str(record.document_type).lower() == "receipt"
        )

        form_count = sum(
            1
            for record in records
            if str(record.document_type).lower() == "form"
        )

        c1, c2, c3, c4, c5 = st.columns(5)

        c1.metric(
            "📄 Total",
            total
        )

        c2.metric(
            "📄 Resume",
            resume_count
        )

        c3.metric(
            "🧾 Invoice",
            invoice_count
        )

        c4.metric(
            "🧾 Receipt",
            receipt_count
        )

        c5.metric(
            "📋 Form",
            form_count
        )

        st.divider()

        # ------------------------------------------
        # No Records
        # ------------------------------------------

        if not records:

            st.info(
                "No documents have been processed yet."
            )

        else:

            # --------------------------------------
            # Records Table
            # --------------------------------------

            st.subheader("🗄 Stored Documents")

            table_data = []

            for record in records:

                table_data.append(
                    {
                        "ID": record.id,
                        "File Name": record.file_name,
                        "Document Type": str(
                            record.document_type
                        ).title(),
                        "Confidence": (
                            f"{record.confidence:.2f}%"
                            if record.confidence is not None
                            else "N/A"
                        ),
                    }
                )

            st.dataframe(
                table_data,
                use_container_width=True,
                hide_index=True,
            )

            st.divider()

            # --------------------------------------
            # Record Details
            # --------------------------------------

            st.subheader("🔍 Record Details")

            record_options = {
                f"#{record.id} — {record.file_name}": record.id
                for record in records
            }

            selected_label = st.selectbox(
                "Select a document",
                list(record_options.keys()),
            )

            selected_id = record_options[
                selected_label
            ]

            selected_record = crud.get(
                selected_id
            )

            if selected_record:

                d1, d2, d3 = st.columns(3)

                d1.metric(
                    "Record ID",
                    selected_record.id
                )

                d2.metric(
                    "Document Type",
                    str(
                        selected_record.document_type
                    ).title()
                )

                d3.metric(
                    "Confidence",
                    (
                        f"{selected_record.confidence:.2f}%"
                        if selected_record.confidence is not None
                        else "N/A"
                    )
                )

                st.write(
                    f"**File Name:** "
                    f"{selected_record.file_name}"
                )

                # ----------------------------------
                # Raw OCR
                # ----------------------------------

                with st.expander(
                    "📄 View Raw OCR Text"
                ):

                    st.text(
                        selected_record.raw_text
                        or "No OCR text stored."
                    )

                # ----------------------------------
                # Complete JSON
                # ----------------------------------

                with st.expander(
                    "🔎 View Complete Extracted JSON"
                ):

                    try:

                        import json

                        json_data = json.loads(
                            selected_record.json_data
                        )

                        st.json(
                            json_data,
                            expanded=True
                        )

                    except Exception:

                        st.text(
                            selected_record.json_data
                            or "No JSON data stored."
                        )

                # ----------------------------------
                # Delete
                # ----------------------------------

                st.divider()

                st.subheader("⚠️ Record Management")

                delete_confirm = st.checkbox(
                    "I understand that deleting this record cannot be undone.",
                    key=f"delete_confirm_{selected_record.id}",
                )

                if st.button(
                    "🗑 Delete Selected Record",
                    type="secondary",
                    disabled=not delete_confirm,
                    use_container_width=True,
                ):

                    deleted = crud.delete(
                        selected_record.id
                    )

                    if deleted:

                        st.success(
                            "Record deleted successfully."
                        )

                        st.rerun()

                    else:

                        st.error(
                            "Record could not be deleted."
                        )

    except Exception as exc:

        st.error(
            "❌ Database operation failed."
        )

        with st.expander("Technical Error"):
            st.exception(exc)

    finally:

        crud.close()