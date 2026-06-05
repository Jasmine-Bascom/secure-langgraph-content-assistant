import re

from langchain_core.messages import AIMessage

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
    Runs before routing. Blocks obvious prompt-injection or tool-manipulation attempts.
    """
    user_input = state["user_input"]

    for pattern in PROMPT_INJECTION_PATTERNS:
        if re.search(pattern, user_input):
            blocked_message = (
                "I can’t help with requests that attempt to bypass instructions, "
                "reveal hidden prompts, manipulate routing, or force tool use."
            )

            return {
                "security_status": "block",
                "security_reason": f"Matched suspicious input pattern: {pattern}",
                "output": blocked_message,
                "messages": [AIMessage(content=blocked_message)],
            }

    return {
        "security_status": "allow",
        "security_reason": "No obvious prompt-injection pattern detected.",
    }


def security_gate(state: CopyWriter) -> str:
    """
    Decides whether to continue to the router or stop.
    """
    if state.get("security_status") == "block":
        return "blocked"

    return "allowed"


def output_validator_node(state: CopyWriter):
    """
    Runs after an agent produces output. Checks for secret-like strings and route-specific constraints.
    """
    output = state.get("output", "") or ""
    route = state.get("route", "")

    for pattern in SECRET_PATTERNS:
        if re.search(pattern, output):
            safe_output = "[Output blocked: potential secret or credential-like value detected.]"

            return {
                "validation_status": "fail",
                "validation_reason": f"Matched potential secret pattern: {pattern}",
                "output": safe_output,
                "messages": [AIMessage(content=safe_output)],
            }

    if route == "x_blog_writer" and len(output) > 280:
        return {
            "validation_status": "warning",
            "validation_reason": f"X/Twitter output is {len(output)} characters, which exceeds 280.",
        }

    return {
        "validation_status": "pass",
        "validation_reason": "Output passed validation checks.",
    }