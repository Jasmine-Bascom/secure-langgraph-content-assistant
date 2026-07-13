from dataclasses import dataclass, field
from typing import Any

from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine


@dataclass
class PiiRedactionResult:
    original_text: str
    redacted_text: str
    entities: list[dict[str, Any]] = field(default_factory=list)


_analyzer: AnalyzerEngine | None = None
_anonymizer: AnonymizerEngine | None = None


def get_analyzer() -> AnalyzerEngine:
    global _analyzer

    if _analyzer is None:
        _analyzer = AnalyzerEngine()

    return _analyzer


def get_anonymizer() -> AnonymizerEngine:
    global _anonymizer

    if _anonymizer is None:
        _anonymizer = AnonymizerEngine()

    return _anonymizer


def redact_pii(text: str) -> PiiRedactionResult:
    """
    Detects and redacts PII from text using Presidio.
    """
    if not text.strip():
        return PiiRedactionResult(
            original_text=text,
            redacted_text=text,
            entities=[],
        )

    analyzer = get_analyzer()
    anonymizer = get_anonymizer()

    analyzer_results = analyzer.analyze(
        text=text,
        language="en",
    )

    anonymized = anonymizer.anonymize(
        text=text,
        analyzer_results=analyzer_results,
    )

    entities = [
        {
            "entity_type": result.entity_type,
            "start": result.start,
            "end": result.end,
            "score": result.score,
        }
        for result in analyzer_results
    ]

    return PiiRedactionResult(
        original_text=text,
        redacted_text=anonymized.text,
        entities=entities,
    )
