from dataclasses import dataclass, field
from typing import Any

from openai import OpenAI


@dataclass
class ModerationDecision:
    flagged: bool
    categories: dict[str, Any] = field(default_factory=dict)
    category_scores: dict[str, Any] = field(default_factory=dict)
    reason: str = ""


def get_client() -> OpenAI:
    """
    Create the OpenAI client only when moderation is actually used.

    This avoids requiring OPENAI_API_KEY merely to import
    the LangGraph application package.
    """
    return OpenAI()


def moderate_text(text: str) -> ModerationDecision:
    """
    Calls OpenAI's moderation endpoint and returns a simplified decision object.
    """
    if not text.strip():
        return ModerationDecision(
            flagged=False,
            reason="Empty input; moderation skipped.",
        )

    client = get_client()

    response = client.moderations.create(
        model="omni-moderation-latest",
        input=text,
    )

    result = response.results[0]

    return ModerationDecision(
        flagged=result.flagged,
        categories=dict(result.categories),
        category_scores=dict(result.category_scores),
        reason="OpenAI moderation completed.",
    )
