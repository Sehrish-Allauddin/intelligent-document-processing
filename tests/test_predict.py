import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.classification.predict import Predictor

predictor = Predictor()

result = predictor.predict(
    "datasets/business_documents/test/invoice/X00016469670.jpg"
)

print(result)