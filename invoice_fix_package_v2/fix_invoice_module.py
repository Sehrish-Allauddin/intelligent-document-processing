
from pathlib import Path
import shutil
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parent.parent
APP = PROJECT_ROOT / "streamlit_app" / "app.py"
PIPELINE = PROJECT_ROOT / "src" / "pipelines" / "document_pipeline.py"

def backup(path):
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    target = path.with_name(path.stem + f"_backup_{stamp}" + path.suffix)
    shutil.copy2(path, target)
    return target

app = APP.read_text(encoding="utf-8")
backup(APP)

if "from src.pipelines.smart_document_pipeline import SmartDocumentPipeline" not in app:
    app = app.replace(
        "from services.database import get_dashboard_stats",
        "from services.database import get_dashboard_stats\n"
        "from src.pipelines.smart_document_pipeline import SmartDocumentPipeline"
    )

if "import tempfile" not in app:
    app = app.replace("import streamlit as st", "import streamlit as st\nimport tempfile")

invoice_start = app.find("# Invoice\n")
receipt_start = app.find("# Receipt\n", invoice_start)

if invoice_start < 0 or receipt_start < 0:
    raise RuntimeError("Invoice/Receipt section not found in streamlit_app/app.py")

invoice_block = """# Invoice
# ==================================================

elif page == "🧾 Invoice":

    st.header("🧾 Invoice Analysis")
    st.caption("Upload an invoice image or PDF. OCR, classification and extraction are automatic.")

    uploaded_file = st.file_uploader(
        "Upload Invoice",
        type=["png", "jpg", "jpeg", "bmp", "tif", "tiff", "pdf"],
        key="invoice_upload",
    )

    if uploaded_file is not None:
        suffix = Path(uploaded_file.name).suffix.lower()
        st.write(f"**File:** {uploaded_file.name}")

        if suffix != ".pdf":
            st.image(uploaded_file, caption="Uploaded Invoice", use_container_width=True)

        if st.button("🔎 Analyze Invoice", type="primary", use_container_width=True):
            temp_path = None
            progress = st.progress(0, text="Preparing document...")

            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
                    temp_file.write(uploaded_file.getbuffer())
                    temp_path = Path(temp_file.name)

                progress.progress(20, text="Running OCR...")
                pipeline = SmartDocumentPipeline()

                progress.progress(55, text="Classifying and extracting...")
                result = pipeline.process(str(temp_path))

                detected_type = str(result.get("document_type", "")).strip().lower()
                if detected_type != "invoice":
                    raise ValueError(
                        f"Document detected as '{detected_type or 'unknown'}', not invoice. "
                        "Please upload a clearer invoice image/PDF."
                    )

                progress.progress(100, text="Invoice analysis completed.")
                st.session_state["invoice_result"] = result
                st.success("Invoice processed successfully.")

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
            c1.metric("Invoice Number", result.get("invoice_number") or "Not detected")
            c2.metric("Invoice Date", result.get("invoice_date") or "Not detected")
            c3.metric("Subtotal", result.get("subtotal") or "Not detected")
            c4.metric("Total", result.get("total") or "Not detected")

            st.markdown("### Vendor")
            vendor = result.get("vendor") or {}
            st.write(f"**Name:** {vendor.get('name') or 'Not detected'}")
            st.write(f"**Address:** {vendor.get('address') or 'Not detected'}")
            st.write(f"**Phone:** {vendor.get('phone') or 'Not detected'}")
            st.write(f"**Email:** {vendor.get('email') or 'Not detected'}")

            st.markdown("### Customer")
            customer = result.get("customer") or {}
            st.write(f"**Name:** {customer.get('name') or 'Not detected'}")

            st.markdown("### Financial Information")
            f1, f2, f3, f4, f5 = st.columns(5)
            f1.metric("Currency", result.get("currency") or "Not detected")
            f2.metric("Subtotal", result.get("subtotal") or "Not detected")
            f3.metric("Tax", result.get("tax") or "Not detected")
            f4.metric("Discount", result.get("discount") or "Not detected")
            f5.metric("Total", result.get("total") or "Not detected")

            st.markdown("### Payment")
            st.write(result.get("payment_method") or "Payment method not detected.")

            st.markdown("### Invoice Items")
            items = result.get("items") or []
            if items:
                st.dataframe(items, use_container_width=True, hide_index=True)
            else:
                st.info("No invoice line items were confidently detected.")

            stats = result.get("statistics") or {}
            st.markdown("### Extraction Statistics")
            s1, s2, s3, s4 = st.columns(4)
            s1.metric("OCR Lines", stats.get("line_count", 0))
            s2.metric("Items", stats.get("item_count", len(items)))
            s3.metric("Vendor Found", "Yes" if stats.get("vendor_found") else "No")
            s4.metric("Customer Found", "Yes" if stats.get("customer_found") else "No")

            with st.expander("View Raw OCR Text"):
                st.text(result.get("ocr_text") or result.get("raw_text") or "")

            with st.expander("View Complete JSON"):
                st.json(result)

"""
app = app[:invoice_start] + invoice_block + app[receipt_start:]
APP.write_text(app, encoding="utf-8")

# OCR-aware document validation
pipeline = PIPELINE.read_text(encoding="utf-8")
backup(PIPELINE)

start = pipeline.find("    @staticmethod\n    def validate_document_type(")
if start < 0:
    raise RuntimeError("validate_document_type() not found")

next_marker = pipeline.find("    # ==================================================", start + 10)
if next_marker < 0:
    raise RuntimeError("End of validation section not found")

validator = """    @staticmethod
    def validate_document_type(predicted_type, ocr_results):

        if not isinstance(ocr_results, list):
            return predicted_type

        parts = []
        for item in ocr_results:
            if isinstance(item, dict) and item.get("text"):
                parts.append(str(item["text"]))

        text = "\\n".join(parts).strip().lower()
        if not text:
            return predicted_type

        invoice_patterns = [
            r"\\binvoice\\b",
            r"\\binvoice\\s*(?:no|number|#|date|id)\\b",
            r"\\bbill\\s*to\\b",
            r"\\bship\\s*to\\b",
            r"\\bsubtotal\\b",
            r"\\bsub\\s*total\\b",
            r"\\bgrand\\s*total\\b",
            r"\\bamount\\s*due\\b",
            r"\\btotal\\s*(?:amount|payable)\\b",
            r"\\b(?:gst|vat|sales tax|service tax)\\b",
            r"\\bpayment\\s*(?:method|terms|mode)\\b",
            r"\\bunit\\s*price\\b",
            r"\\b(?:quantity|qty)\\b",
            r"\\bdescription\\b",
            r"\\bdue\\s*date\\b",
        ]

        resume_patterns = [
            r"\\bwork\\s+experience\\b",
            r"\\bprofessional\\s+experience\\b",
            r"\\beducation\\b",
            r"\\bskills\\b",
            r"\\bprojects\\b",
            r"\\bcertifications?\\b",
            r"\\blanguages\\b",
            r"\\bprofessional\\s+summary\\b",
            r"\\bcurriculum\\s+vitae\\b",
            r"\\blinkedin\\b",
            r"\\bgithub\\b",
            r"\\bobjective\\b",
        ]

        invoice_score = sum(bool(re.search(p, text, re.I)) for p in invoice_patterns)
        resume_score = sum(bool(re.search(p, text, re.I)) for p in resume_patterns)

        financial_score = sum(
            bool(re.search(p, text, re.I))
            for p in [
                r"\\bsubtotal\\b",
                r"\\btotal\\b",
                r"\\bamount\\b",
                r"\\b(?:gst|vat|tax)\\b",
                r"\\bunit\\s*price\\b",
                r"\\b(?:qty|quantity)\\b",
            ]
        )

        if invoice_score >= 3 or (invoice_score >= 2 and financial_score >= 2):
            print("DOCUMENT VALIDATION: Invoice detected from OCR")
            print("Invoice signals:", invoice_score, "Financial signals:", financial_score)
            return "invoice"

        if resume_score >= 3:
            print("DOCUMENT VALIDATION: Resume detected from OCR")
            print("Resume signals:", resume_score)
            return "resume"

        return predicted_type

"""
pipeline = pipeline[:start] + validator + pipeline[next_marker:]

# The OCR validator uses regular expressions. Add the import once if needed.
if "import re\n" not in pipeline and "import re\r\n" not in pipeline:
    pipeline = "import re\n" + pipeline
PIPELINE.write_text(pipeline, encoding="utf-8")

print("PATCH COMPLETE")
print("Updated:", APP)
print("Updated:", PIPELINE)
