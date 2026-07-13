import re

from langchain_core.messages import AIMessage

from src.audit import write_audit_event
from src.moderation import moderate_text
from src.pii import redact_pii
from src.state import CopyWriter


PROMPT_INJECTION_PATTERNS = [
    r"(?i)ignore (all )?(previous|prior) instructions",
    r"(?i)disregard (all )?(previous|prior) instructions",
    r"(?i)reveal (the )?(system|developer) prompt",
    r"(?i)show (the )?(system|developer) prompt",
    r"(?i)bypass (the )?(router|security|validation|guardrails)",
    r"(?i)you are now (the )?(router|system|developer|admin)",
    r"(?i)exfiltrate|leak|dump secrets",
    r"(?i)call .*tool",
    r"(?i)override .*instructions",
]

SECRET_PATTERNS = [
    r"sk-[A-Za-z0-9_-]{20,}",
    r"AKIA[0-9A-Z]{16}",
    r"(?i)api[_-]?key\s*[:=]\s*['\"][^'\"]+['\"]",
    r"(?i)password\s*[:=]\s*['\"][^'\"]+['\"]",
    r"(?i)secret\s*[:=]\s*['\"][^'\"]+['\"]",
]


def security_precheck_node(state: CopyWriter):
    """
    Runs before routing.
    Uses:
    - regex for prompt-injection/tool manipulation patterns
    - OpenAI moderation for harmful-content signals
    - Presidio for PII redaction before routing
    """
    user_input = state["user_input"]

    for pattern in PROMPT_INJECTION_PATTERNS:
        if re.search(pattern, user_input):
            blocked_message = (
                "I can’t help with requests that attempt to bypass instructions, "
                "reveal hidden prompts, manipulate routing, or force tool use."
            )

            write_audit_event(
                "security_precheck_blocked",
                reason="prompt_injection_pattern",
                pattern=pattern,
                user_input=user_input,
            )

            return {
                "security_status": "block",
                "security_reason": f"Matched suspicious input pattern: {pattern}",
                "output": blocked_message,
                "messages": [AIMessage(content=blocked_message)],
            }

    moderation = moderate_text(user_input)

    if moderation.flagged:
        blocked_message = (
            "I can’t process this request because it was flagged by the moderation layer."
        )

        write_audit_event(
            "security_precheck_blocked",
            reason="openai_moderation_flag",
            categories=moderation.categories,
            category_scores=moderation.category_scores,
        )

        return {
            "security_status": "block",
            "security_reason": "OpenAI moderation flagged the input.",
            "output": blocked_message,
            "messages": [AIMessage(content=blocked_message)],
        }

    pii_result = redact_pii(user_input)

    if pii_result.entities:
        write_audit_event(
            "pii_redacted_input",
            entity_types=[entity["entity_type"] for entity in pii_result.entities],
            entity_count=len(pii_result.entities),
        )

        return {
            "user_input": pii_result.redacted_text,
            "security_status": "allow",
            "security_reason": (
                f"Input allowed after PII redaction. "
                f"Redacted {len(pii_result.entities)} PII entities."
            ),
        }

    write_audit_event(
        "security_precheck_allowed",
        reason="no_prompt_injection_no_moderation_flag_no_pii",
    )

    return {
        "security_status": "allow",
        "security_reason": "Input passed prompt-injection, moderation, and PII checks.",
    }


def security_gate(state: CopyWriter) -> str:
    if state.get("security_status") == "block":
        return "blocked"

    return "allowed"


def output_validator_node(state: CopyWriter):
    """
    Runs after an agent produces output.
    Uses:
    - regex for secret-like strings
    - OpenAI moderation for generated output
    - Presidio for PII redaction in generated output
    - X/Twitter length validation
    """
    output = state.get("output", "") or ""
    route = state.get("route", "")

    for pattern in SECRET_PATTERNS:
        if re.search(pattern, output):
            safe_output = "[Output blocked: potential secret or credential-like value detected.]"

            write_audit_event(
                "output_validation_failed",
                reason="secret_pattern",
                pattern=pattern,
                route=route,
            )

            return {
                "validation_status": "fail",
                "validation_reason": f"Matched potential secret pattern: {pattern}",
                "output": safe_output,
                "messages": [AIMessage(content=safe_output)],
            }

    moderation = moderate_text(output)

    if moderation.flagged:
        safe_output = "[Output blocked: generated content was flagged by moderation.]"

        write_audit_event(
            "output_validation_failed",
            reason="openai_moderation_flag",
            route=route,
            categories=moderation.categories,
            category_scores=moderation.category_scores,
        )

        return {
            "validation_status": "fail",
            "validation_reason": "OpenAI moderation flagged the generated output.",
            "output": safe_output,
            "messages": [AIMessage(content=safe_output)],
        }

    pii_result = redact_pii(output)

    if pii_result.entities:
        write_audit_event(
            "pii_redacted_output",
            route=route,
            entity_types=[entity["entity_type"] for entity in pii_result.entities],
            entity_count=len(pii_result.entities),
        )

        return {
            "validation_status": "warning",
            "validation_reason": (
                f"Output contained PII-like values; redacted "
                f"{len(pii_result.entities)} entities."
            ),
            "output": pii_result.redacted_text,
            "messages": [AIMessage(content=pii_result.redacted_text)],
        }

    if route == "x_blog_writer" and len(output) > 280:
        write_audit_event(
            "output_validation_warning",
            reason="x_post_length_exceeded",
            route=route,
            character_count=len(output),
        )

        return {
            "validation_status": "warning",
            "validation_reason": (
                f"X/Twitter output is {len(output)} characters, which exceeds 280."
            ),
        }

    write_audit_event(
        "output_validation_passed",
        route=route,
    )

    return {
        "validation_status": "pass",
        "validation_reason": "Output passed secret, moderation, PII, and format checks.",
    }