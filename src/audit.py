import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


LOG_DIR = Path("logs")
LOG_PATH = LOG_DIR / "audit.jsonl"


def setup_audit_logger() -> logging.Logger:
    LOG_DIR.mkdir(exist_ok=True)

    logger = logging.getLogger("secure_langgraph_audit")
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        handler = logging.FileHandler(LOG_PATH)
        handler.setFormatter(logging.Formatter("%(message)s"))
        logger.addHandler(handler)

    return logger


audit_logger = setup_audit_logger()


def write_audit_event(event_type: str, **fields: Any) -> None:
    event = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event_type": event_type,
        **fields,
    }

    audit_logger.info(json.dumps(event, default=str))