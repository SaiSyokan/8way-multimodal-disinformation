"""Common eight-way evaluator used for OctantAgent and normalized baselines."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .io import dump_json, load_jsonl
from .labels import LABELS


def evaluate_predictions(path: str | Path, output: str | Path | None = None) -> dict[str, Any]:
    rows = load_jsonl(path)
    counts = {label: {"tp": 0, "fp": 0, "fn": 0, "support": 0} for label in LABELS}
    correct = 0
    invalid = 0
    for line, row in enumerate(rows, 1):
        gold = str(row.get("gold_label", row.get("label", ""))).strip().upper()
        if gold not in LABELS:
            raise ValueError(f"{path}:{line}: invalid or missing gold label {gold!r}")
        raw_prediction = row.get("prediction")
        prediction = str(raw_prediction).strip().upper() if raw_prediction is not None else ""
        counts[gold]["support"] += 1
        if prediction not in LABELS:
            invalid += 1
            counts[gold]["fn"] += 1
            continue
        if prediction == gold:
            correct += 1
            counts[gold]["tp"] += 1
        else:
            counts[gold]["fn"] += 1
            counts[prediction]["fp"] += 1

    per_class: dict[str, dict[str, float | int]] = {}
    for label in LABELS:
        value = counts[label]
        precision_denominator = value["tp"] + value["fp"]
        recall_denominator = value["tp"] + value["fn"]
        precision = value["tp"] / precision_denominator if precision_denominator else 0.0
        recall = value["tp"] / recall_denominator if recall_denominator else 0.0
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
        per_class[label] = {
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "support": value["support"],
        }
    result: dict[str, Any] = {
        "total": len(rows),
        "correct": correct,
        "invalid_predictions": invalid,
        "accuracy": correct / len(rows) if rows else 0.0,
        "macro_precision": sum(float(per_class[x]["precision"]) for x in LABELS) / len(LABELS),
        "macro_recall": sum(float(per_class[x]["recall"]) for x in LABELS) / len(LABELS),
        "macro_f1": sum(float(per_class[x]["f1"]) for x in LABELS) / len(LABELS),
        "per_class": per_class,
    }
    if output is not None:
        dump_json(output, result)
    return result
