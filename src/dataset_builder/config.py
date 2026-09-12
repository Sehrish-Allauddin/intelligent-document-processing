from pathlib import Path

# Project Root
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Original Datasets
DATASETS = {
    "rvl_cdip": PROJECT_ROOT / "datasets" / "rvl_cdip",
    "invoice": PROJECT_ROOT / "datasets" / "invoice",
    "receipt": PROJECT_ROOT / "datasets" / "receipt",
    "resumes": PROJECT_ROOT / "datasets" / "resume_images",
    "funsd": PROJECT_ROOT / "datasets" / "funsd",
    "sroie": PROJECT_ROOT / "datasets" / "sroie",
}

# Output Dataset
OUTPUT_DATASET = PROJECT_ROOT / "datasets" / "business_documents"