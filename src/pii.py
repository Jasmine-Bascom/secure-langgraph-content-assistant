from dataclasses import dataclass, field
from typing import Any

from presidio_analyzer import AnalyzerEngine
from presidio_analyzer.nlp_engine import NlpEngineProvider
from presidio_anonymizer import AnonymizerEngine


@dataclass
class PiiRedactionResult:
    original_text: str
    redacted_text: str
    entities: list[dict[str, Any]] = field(
        default_factory=list
    )


_analyzer: AnalyzerEngine | None = None
_anonymizer: AnonymizerEngine | None = None


def get_analyzer() -> AnalyzerEngine:
    """
    Build Presidio with an explicit, lightweight spaCy model.

    Using an explicit NLP configuration avoids relying on
    Presidio's default model setup and makes cloud deployment
    deterministic.
    """

    global _analyzer

    if _analyzer is None:
        configuration = {
            "nlp_engine_name": "spacy",
            "models": [
                {
                    "lang_code": "en",
                    "model_name": "en_core_web_sm",
                }
            ],
        }

        provider = NlpEngineProvider(
            nlp_configuration=configuration
        )

        nlp_engine = (
            provider.create_engine()
        )

        _analyzer = AnalyzerEngine(
            nlp_engine=nlp_engine,
            supported_languages=["en"],
        )

    return _analyzer


def get_anonymizer() -> AnonymizerEngine:
    """
    Lazily construct the Presidio anonymizer.
    """

    global _anonymizer

    if _anonymizer is None:
        _anonymizer = (
            AnonymizerEngine()
        )

    return _anonymizer


def redact_pii(
    text: str,
) -> PiiRedactionResult:
    """
    Detect and redact PII using Presidio.

    The analyzer is initialized lazily so importing the
    LangGraph application does not immediately load spaCy.
    """

    if not text.strip():
        return PiiRedactionResult(
            original_text=text,
            redacted_text=text,
            entities=[],
        )

    analyzer = get_analyzer()
    anonymizer = get_anonymizer()

    analyzer_results = (
        analyzer.analyze(
            text=text,
            language="en",
        )
    )

    anonymized = (
        anonymizer.anonymize(
            text=text,
            analyzer_results=(
                analyzer_results
            ),
        )
    )

    entities = [
        {
            "entity_type": (
                result.entity_type
            ),
            "start": result.start,
            "end": result.end,
            "score": result.score,
        }
        for result in analyzer_results
    ]

    return PiiRedactionResult(
        original_text=text,
        redacted_text=(
            anonymized.text
        ),
        entities=entities,
    )