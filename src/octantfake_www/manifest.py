"""Manifest validation and summary utilities."""

from __future__ import annotations

from collections import Counter
import hashlib
from pathlib import Path
from typing import Any

from .io import load_jsonl, validate_identifier
from .labels import LABELS, label_from_factors


REQUIRED_FIELDS = {
    "sample_id",
    "image_id",
    "image_path",
    "text_id",
    "text",
    "image_veracity",
    "text_veracity",
    "image_text_consistency",
    "label",
    "image_source",
    "text_source",
    "construction_type",
    "split",
}


def validate_manifest(
    path: str | Path,
    check_files: bool = False,
    media_root: str | Path | None = None,
) -> dict[str, Any]:
    rows = load_jsonl(path)
    errors: list[str] = []
    warnings: list[str] = []
    sample_ids: set[str] = set()
    image_ids: set[str] = set()
    text_ids: set[str] = set()
    image_paths: set[str] = set()
    text_values: Counter[str] = Counter()
    image_hashes: Counter[str] = Counter()
    labels: Counter[str] = Counter()
    splits: Counter[str] = Counter()
    base = (
        Path(media_root).expanduser().resolve()
        if media_root is not None
        else Path(path).expanduser().resolve().parent
    )

    for line, row in enumerate(rows, 1):
        missing = REQUIRED_FIELDS.difference(row)
        if missing:
            errors.append(f"line {line}: missing {', '.join(sorted(missing))}")
            continue
        try:
            sample_id = validate_identifier(row["sample_id"], "sample_id")
        except ValueError as exc:
            errors.append(f"line {line}: {exc}")
            sample_id = str(row["sample_id"])
        if sample_id in sample_ids:
            errors.append(f"line {line}: duplicate sample_id {sample_id!r}")
        sample_ids.add(sample_id)
        image_id = str(row["image_id"])
        text_id = str(row["text_id"])
        if image_id in image_ids:
            errors.append(f"line {line}: reused image_id {image_id!r}")
        if text_id in text_ids:
            errors.append(f"line {line}: reused text_id {text_id!r}")
        image_ids.add(image_id)
        text_ids.add(text_id)
        image_value = Path(str(row["image_path"])).expanduser()
        image_key = str(
            image_value.resolve() if image_value.is_absolute() else (base / image_value).resolve()
        )
        text_key = " ".join(str(row["text"]).casefold().split())
        if image_key in image_paths:
            errors.append(f"line {line}: reused image content path {image_key!r}")
        image_paths.add(image_key)
        text_values[text_key] += 1
        declared_hash = str(row.get("image_sha256", "")).lower()
        if declared_hash:
            if len(declared_hash) != 64 or any(character not in "0123456789abcdef" for character in declared_hash):
                errors.append(f"line {line}: invalid image_sha256")
            else:
                image_hashes[declared_hash] += 1
        try:
            derived = label_from_factors(
                row["image_veracity"], row["text_veracity"], row["image_text_consistency"]
            )
            label = str(row["label"]).upper()
            if label != derived:
                errors.append(f"line {line}: label {label!r} disagrees with factors ({derived})")
            if label not in LABELS:
                errors.append(f"line {line}: invalid label {label!r}")
            else:
                labels[label] += 1
        except ValueError as exc:
            errors.append(f"line {line}: {exc}")
        split = str(row["split"])
        if split not in {"calibration", "test"}:
            errors.append(f"line {line}: invalid split {split!r}")
        else:
            splits[split] += 1
        if not str(row["text"]).strip():
            errors.append(f"line {line}: empty text")
        if check_files:
            image = Path(str(row["image_path"])).expanduser()
            if not image.is_absolute():
                image = base / image
            if not image.is_file():
                errors.append(f"line {line}: image does not exist: {image}")
            elif declared_hash:
                digest = hashlib.sha256()
                with image.open("rb") as handle:
                    for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                        digest.update(chunk)
                if digest.hexdigest() != declared_hash:
                    errors.append(f"line {line}: image checksum mismatch: {image}")

    repeated_text_groups = sum(count > 1 for count in text_values.values())
    repeated_text_copies = sum(count - 1 for count in text_values.values() if count > 1)
    repeated_image_groups = sum(count > 1 for count in image_hashes.values())
    repeated_image_copies = sum(count - 1 for count in image_hashes.values() if count > 1)
    if repeated_text_groups:
        warnings.append(
            f"{repeated_text_groups} repeated normalized-text groups "
            f"({repeated_text_copies} additional records)"
        )
    if repeated_image_groups:
        warnings.append(
            f"{repeated_image_groups} byte-identical image groups "
            f"({repeated_image_copies} additional records)"
        )

    return {
        "valid": not errors,
        "total": len(rows),
        "labels": dict(sorted(labels.items())),
        "splits": dict(sorted(splits.items())),
        "warnings": warnings,
        "errors": errors,
    }
