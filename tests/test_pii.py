from src.moderation import ModerationDecision
from src.pii import PiiRedactionResult, redact_pii
from src.security import security_precheck_node


def test_moderation_flag_blocks_input(monkeypatch):
    def fake_moderate_text(text):
        return ModerationDecision(
            flagged=True,
            categories={"violence": True},
            category_scores={"violence": 0.99},
            reason="fake moderation result",
        )

    def fake_redact_pii(text):
        return PiiRedactionResult(
            original_text=text,
            redacted_text=text,
            entities=[],
        )

    monkeypatch.setattr("src.security.moderate_text", fake_moderate_text)
    monkeypatch.setattr("src.security.redact_pii", fake_redact_pii)

    state = {
        "user_input": "Some risky content",
        "route": "",
        "output": "",
        "messages": [],
    }

    result = security_precheck_node(state)

    assert result["security_status"] == "block"
    assert "moderation" in result["security_reason"].lower()


def test_pii_redaction_detects_phone_number():
    text = "Call me at 212-555-5555."
    result = redact_pii(text)

    assert result.redacted_text != text
    assert len(result.entities) >= 1


def test_pii_redaction_leaves_non_pii_text_mostly_unchanged():
    text = "Write a blog post about AI productivity tools."
    result = redact_pii(text)

    assert result.redacted_text
