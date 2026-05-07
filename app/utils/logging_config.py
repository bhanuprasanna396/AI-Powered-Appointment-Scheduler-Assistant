import json
import logging
import os
from typing import Any, Dict


def configure_logging() -> None:
    level = os.getenv("LOG_LEVEL", "INFO").upper()
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


def log_stage(logger: logging.Logger, stage: str, payload: Dict[str, Any]) -> None:
    logger.info("stage=%s payload=%s", stage, json.dumps(payload, ensure_ascii=True))
