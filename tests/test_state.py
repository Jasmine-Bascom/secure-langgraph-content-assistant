from typing import get_type_hints

from src.state import CopyWriter


def test_copywriter_state_has_expected_fields():
    hints = get_type_hints(CopyWriter, include_extras=True)

    assert "user_input" in hints
    assert "route" in hints
    assert "output" in hints
    assert "messages" in hints
    assert "security_status" in hints
    assert "security_reason" in hints
    assert "validation_status" in hints
    assert "validation_reason" in hints
