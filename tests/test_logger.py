import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.utils.logger import get_logger

logger = get_logger()

logger.info("Training Started")

logger.warning("GPU Memory Low")

logger.error("Dummy Error")

print("Logger Working")