"""Typed records shared by dataset construction and inference."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Mapping, Optional

from .labels import label_from_factors


@dataclass(frozen=True)
class ImageRecord:
    source_id: str
    path: str
    source: str
    veracity: str
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class TextRecord:
    source_id: str
    text: str
    source: str
    veracity: str
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class PairRecord:
    sample_id: str
    image_id: str
    image_path: str
    text_id: str
    text: str
    image_veracity: str
    text_veracity: str
    image_text_consistency: str
    image_source: str
    text_source: str
    construction_type: str = "source_native"
    split: Optional[str] = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    @property
    def label(self) -> str:
        return label_from_factors(
            self.image_veracity,
            self.text_veracity,
            self.image_text_consistency,
        )

    def to_dict(self) -> dict[str, Any]:
        value = asdict(self)
        value["label"] = self.label
        return value

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> "PairRecord":
        fields = {
            "sample_id",
            "image_id",
            "image_path",
            "text_id",
            "text",
            "image_veracity",
            "text_veracity",
            "image_text_consistency",
            "image_source",
            "text_source",
            "construction_type",
            "split",
            "metadata",
        }
        record = cls(**{key: value[key] for key in fields if key in value})
        if "label" in value and str(value["label"]).upper() != record.label:
            raise ValueError(
                f"sample {record.sample_id}: label {value['label']!r} disagrees with {record.label}"
            )
        return record


@dataclass(frozen=True)
class FactorResult:
    decision: str
    confidence: float
    explanation: str
    raw_output: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class PredictionRecord:
    sample_id: str
    prediction: Optional[str]
    image_result: Optional[FactorResult]
    text_result: Optional[FactorResult]
    consistency_result: Optional[FactorResult]
    aggregator_output: str
    image_description: str = ""
    consistency_description: str = ""
    prompt_version: str = "www26-v1"
    aggregator_confidence: Optional[float] = None
    aggregator_explanation: str = ""
    factor_label: Optional[str] = None
    error: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
