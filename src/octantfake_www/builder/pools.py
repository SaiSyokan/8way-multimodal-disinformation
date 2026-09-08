"""Load normalized single-modality candidate manifests."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ..io import load_jsonl
from ..labels import normalize_factor
from ..records import ImageRecord, TextRecord


def load_image_pool(path: str | Path) -> list[ImageRecord]:
    base = Path(path).expanduser().resolve().parent
    records: list[ImageRecord] = []
    for index, row in enumerate(load_jsonl(path), 1):
        required = {"id", "path", "source", "veracity"}
        missing = required.difference(row)
        if missing:
            raise ValueError(f"{path}:{index}: missing {', '.join(sorted(missing))}")
        image = Path(str(row["path"])).expanduser()
        if not image.is_absolute():
            image = base / image
        if not image.is_file():
            continue
        records.append(
            ImageRecord(
                source_id=str(row["id"]),
                path=str(image.resolve()),
                source=str(row["source"]),
                veracity=normalize_factor(row["veracity"], "image veracity"),
                metadata=_metadata(row, required),
            )
        )
    return records


def load_text_pool(path: str | Path) -> list[TextRecord]:
    records: list[TextRecord] = []
    for index, row in enumerate(load_jsonl(path), 1):
        required = {"id", "text", "source", "veracity"}
        missing = required.difference(row)
        if missing:
            raise ValueError(f"{path}:{index}: missing {', '.join(sorted(missing))}")
        text = str(row["text"]).strip()
        if not text:
            continue
        records.append(
            TextRecord(
                source_id=str(row["id"]),
                text=text,
                source=str(row["source"]),
                veracity=normalize_factor(row["veracity"], "text veracity"),
                metadata=_metadata(row, required),
            )
        )
    return records


def _metadata(row: dict[str, Any], required: set[str]) -> dict[str, Any]:
    metadata = row.get("metadata", {})
    if not isinstance(metadata, dict):
        raise ValueError("metadata must be a JSON object")
    extras = {key: value for key, value in row.items() if key not in required | {"metadata"}}
    return {**metadata, **extras}
