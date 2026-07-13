from pathlib import Path

from src.audit import write_audit_event


def test_audit_log_writes_jsonl_event():
    write_audit_event("test_event", status="ok")

    log_path = Path("logs/audit.jsonl")

    assert log_path.exists()
    text = log_path.read_text()
    assert "test_event" in text
    assert '"status": "ok"' in text
