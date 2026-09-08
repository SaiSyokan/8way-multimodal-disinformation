"""Evidence-guided OctantAgent orchestration."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Protocol

from ..evidence.store import EvidenceStore
from ..records import PredictionRecord
from .parser import parse_factor, parse_label
from .prompts import (
    AGGREGATOR_PROMPT,
    CONSISTENCY_PROMPT,
    CONSISTENCY_DESCRIPTION_PROMPT,
    DESCRIPTION_PROMPT,
    IMAGE_PROMPT,
    TEXT_PROMPT,
)


class Backend(Protocol):
    def generate(self, prompt: str, image_path: str | Path | None = None) -> str: ...


class OctantAgent:
    """Run description, three factor checks, and the final 8-way aggregator."""

    def __init__(self, backend: Backend, evidence: EvidenceStore) -> None:
        self.backend = backend
        self.evidence = evidence

    def predict(self, row: dict[str, object], manifest_root: str | Path = ".") -> PredictionRecord:
        sample_id = str(row["sample_id"])
        image_path = Path(str(row["image_path"])).expanduser()
        if not image_path.is_absolute():
            image_path = Path(manifest_root) / image_path
        image_result = None
        text_result = None
        consistency_result = None
        aggregator_output = ""
        image_description = ""
        consistency_description = ""
        try:
            text = str(row["text"])
            image_description = self.backend.generate(DESCRIPTION_PROMPT, image_path)
            consistency_description = self.backend.generate(
                CONSISTENCY_DESCRIPTION_PROMPT, image_path
            )
            text_value = self.evidence.text(sample_id)
            image_value = self.evidence.image(sample_id)
            text_evidence = self.evidence.render_text(text_value)
            image_evidence = self.evidence.render_image(image_value)
            image_result = parse_factor(
                self.backend.generate(
                    IMAGE_PROMPT.format(
                        description=image_description, image_evidence=image_evidence
                    ),
                    image_path,
                )
            )
            text_result = parse_factor(
                self.backend.generate(
                    TEXT_PROMPT.format(text=text, text_evidence=text_evidence), None
                )
            )
            consistency_result = parse_factor(
                self.backend.generate(
                    CONSISTENCY_PROMPT.format(
                        text=text,
                        description=consistency_description,
                    ),
                    image_path,
                )
            )
            aggregator_output = self.backend.generate(
                AGGREGATOR_PROMPT.format(
                    image_result=json.dumps(image_result.to_dict(), ensure_ascii=False),
                    text_result=json.dumps(text_result.to_dict(), ensure_ascii=False),
                    consistency_result=json.dumps(
                        consistency_result.to_dict(), ensure_ascii=False
                    ),
                ),
                None,
            )
            prediction, aggregator_confidence, aggregator_explanation = parse_label(
                aggregator_output
            )
            factor_label = (
                image_result.decision
                + text_result.decision
                + consistency_result.decision
            )
            return PredictionRecord(
                sample_id=sample_id,
                prediction=prediction,
                image_result=image_result,
                text_result=text_result,
                consistency_result=consistency_result,
                aggregator_output=aggregator_output,
                image_description=image_description,
                consistency_description=consistency_description,
                aggregator_confidence=aggregator_confidence,
                aggregator_explanation=aggregator_explanation,
                factor_label=factor_label,
            )
        except Exception as exc:
            return PredictionRecord(
                sample_id=sample_id,
                prediction=None,
                image_result=image_result,
                text_result=text_result,
                consistency_result=consistency_result,
                aggregator_output=aggregator_output,
                image_description=image_description,
                consistency_description=consistency_description,
                error=str(exc),
            )
