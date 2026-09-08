"""Strict parsers that never turn malformed outputs into the majority class."""

from __future__ import annotations

import json
import re
from typing import Any

from ..labels import LABELS
from ..records import FactorResult


def _json_object(raw: str) -> dict[str, Any]:
    try:
        value = json.loads(raw)
        if isinstance(value, dict):
            return value
    except json.JSONDecodeError:
        pass
    for match in re.finditer(r"\{.*?\}", raw, flags=re.DOTALL):
        try:
            value = json.loads(match.group(0))
            if isinstance(value, dict):
                return value
        except json.JSONDecodeError:
            continue
    raise ValueError("model output does not contain a valid JSON object")


def parse_factor(raw: str) -> FactorResult:
    value = _json_object(raw)
    decision = str(value.get("decision", "")).strip().upper()
    decision = {"TRUE": "T", "FALSE": "F"}.get(decision, decision)
    if decision not in {"T", "F"}:
        raise ValueError(f"invalid factor decision: {decision!r}")
    try:
        confidence = float(value.get("confidence"))
    except (TypeError, ValueError) as exc:
        raise ValueError("factor confidence must be numeric") from exc
    if not 0.0 <= confidence <= 1.0:
        raise ValueError("factor confidence must be between 0 and 1")
    explanation = str(value.get("explanation", "")).strip()
    if not explanation:
        raise ValueError("factor explanation must not be empty")
    return FactorResult(decision, confidence, explanation, raw)


def parse_label(raw: str) -> tuple[str, float, str]:
    value = _json_object(raw)
    label = str(value.get("label", "")).strip().upper()
    if label not in LABELS:
        raise ValueError(f"invalid 8-way label: {label!r}")
    try:
        confidence = float(value.get("confidence"))
    except (TypeError, ValueError) as exc:
        raise ValueError("aggregator confidence must be numeric") from exc
    if not 0.0 <= confidence <= 1.0:
        raise ValueError("aggregator confidence must be between 0 and 1")
    explanation = str(value.get("explanation", "")).strip()
    return label, confidence, explanation
