"""Paper-aligned adapters for the original multimodal source layouts."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any, Iterable, Mapping

from ...records import PairRecord


def _objects(path: Path) -> list[dict[str, Any]]:
    """Read a JSON array or a stream of adjacent JSON objects."""

    raw = path.read_text(encoding="utf-8")
    try:
        value = json.loads(raw)
        if isinstance(value, list):
            return [row for row in value if isinstance(row, dict)]
        if isinstance(value, dict):
            return [value]
    except json.JSONDecodeError:
        pass
    decoder = json.JSONDecoder()
    rows: list[dict[str, Any]] = []
    position = 0
    while position < len(raw):
        while position < len(raw) and raw[position].isspace():
            position += 1
        if position >= len(raw):
            break
        value, position = decoder.raw_decode(raw, position)
        if isinstance(value, dict):
            rows.append(value)
    return rows


def _pair(
    source: str,
    index: int,
    root: Path,
    image_path: str | Path,
    text: str,
    factors: tuple[str, str, str],
    original: Mapping[str, Any],
) -> PairRecord | None:
    image = Path(image_path)
    if not image.is_absolute():
        image = root / image
    text = text.strip()
    if not text or not image.is_file():
        return None
    stem = f"{source.lower()}-{index:07d}"
    return PairRecord(
        sample_id=stem,
        image_id=stem + "-image",
        image_path=str(image.resolve()),
        text_id=stem + "-text",
        text=text,
        image_veracity=factors[0],
        text_veracity=factors[1],
        image_text_consistency=factors[2],
        image_source=source,
        text_source=source,
        metadata={"source_row": dict(original)},
    )


def _cosmos(root: Path) -> Iterable[PairRecord]:
    rows = _objects(root / "cosmos_anns" / "test_data.json")
    for index, row in enumerate(rows):
        consistency = "T" if int(row.get("context_label", 0)) == 0 else "F"
        record = _pair(
            "COSMOS",
            index,
            root,
            str(row.get("img_local_path", "")).lstrip("/"),
            str(row.get("caption1_modified", "")),
            ("T", "T", consistency),
            row,
        )
        if record:
            yield record


_DGM4_FACTORS = {
    "orig": ("T", "T", "T"),
    "text_attribute": ("T", "F", "T"),
    "text_swap": ("T", "T", "F"),
    "face_attribute": ("F", "T", "T"),
    "face_swap": ("F", "T", "T"),
    "face_attribute&text_attribute": ("F", "F", "T"),
    "face_swap&text_attribute": ("F", "F", "T"),
    "face_attribute&text_swap": ("F", "T", "F"),
    "face_swap&text_swap": ("F", "T", "F"),
}


def _dgm4_image(root: Path, raw: str) -> Path:
    parts = Path(raw.replace("\\", "/")).parts
    if "DGM4" in parts:
        parts = parts[parts.index("DGM4") + 1 :]
    candidate = root.joinpath(*parts)
    if candidate.is_file():
        return candidate
    alternate = tuple("original" if p == "origin" else "origin" if p == "original" else p for p in parts)
    return root.joinpath(*alternate)


def _dgm4(root: Path) -> Iterable[PairRecord]:
    rows = _objects(root / "metadata" / "test.json")
    for index, row in enumerate(rows):
        fake_class = str(row.get("fake_cls", "")).strip().lower()
        factors = _DGM4_FACTORS.get(fake_class)
        if factors is None:  # Unknown classes must never silently become TTT.
            continue
        record = _pair(
            "DGM4", index, root, _dgm4_image(root, str(row.get("image", ""))),
            str(row.get("text", "")), factors, row,
        )
        if record:
            yield record


def _meir(root: Path, max_text_length: int) -> Iterable[PairRecord]:
    rows = _objects(root / "meir_test_samples.json")
    seen: set[str] = set()
    for index, row in enumerate(rows):
        text = str(row.get("text", "")).strip()
        if not text or len(text) > max_text_length or text in seen:
            continue
        seen.add(text)
        text_factor = "T" if str(row.get("fake_cls", "none")).lower() == "none" else "F"
        record = _pair(
            "MEIR", index, root, str(row.get("image_path", "")), text,
            ("T", text_factor, "T"), row,
        )
        if record:
            yield record


_MMFAKEBENCH_FACTORS = {
    "original": ("T", "T", "T"),
    "textual_veracity_distortion": ("T", "F", "T"),
    "visual_veracity_distortion": ("F", "T", "T"),
    "mismatch": ("T", "T", "F"),
}


def _mmfakebench(root: Path) -> Iterable[PairRecord]:
    rows = _objects(root / "MMFakeBench_test.json")
    for index, row in enumerate(rows):
        factors = _MMFAKEBENCH_FACTORS.get(str(row.get("fake_cls", "")).lower())
        if factors is None:
            continue
        record = _pair(
            "MMFakeBench", index, root,
            root / "MMFakeBench_test" / str(row.get("image_path", "")).lstrip("/"),
            str(row.get("text", "")), factors, row,
        )
        if record:
            yield record


def _newsclippings(root: Path) -> Iterable[PairRecord]:
    visual_root = root / "visual_news"
    visual_rows = _objects(visual_root / "data.json")
    visual_index = {int(row["id"]): row for row in visual_rows if "id" in row}
    value = json.loads((root / "news_clippings" / "test.json").read_text(encoding="utf-8"))
    for index, row in enumerate(value.get("annotations", [])):
        caption_row = visual_index.get(int(row.get("id", -1)))
        image_row = visual_index.get(int(row.get("image_id", -1)))
        if not caption_row or not image_row:
            continue
        consistency = "F" if bool(row.get("falsified")) else "T"
        record = _pair(
            "NewsCLIPpings", index, root,
            visual_root / str(image_row.get("image_path", "")).lstrip("./"),
            str(caption_row.get("caption", "")), ("T", "T", consistency), row,
        )
        if record:
            yield record


_VERITE_FACTORS = {
    "true": ("T", "T", "T"),
    "miscaptioned": ("T", "F", "T"),
    "out-of-context": ("T", "T", "F"),
}


def _verite(root: Path) -> Iterable[PairRecord]:
    with (root / "VERITE.csv").open("r", encoding="utf-8", newline="") as handle:
        for index, row in enumerate(csv.DictReader(handle)):
            factors = _VERITE_FACTORS.get(str(row.get("label", "")).strip().lower())
            if factors is None:
                continue
            record = _pair(
                "VERITE", index, root, str(row.get("image_path", "")).lstrip("/"),
                str(row.get("caption", "")), factors, row,
            )
            if record:
                yield record


def load_multimodal_source(name: str, root: str | Path, max_text_length: int = 160) -> list[PairRecord]:
    """Load one supported source, excluding malformed and unknown-label rows."""

    source_root = Path(root).expanduser()
    normalized = name.strip().lower().replace("-", "").replace("_", "")
    readers = {
        "cosmos": lambda: _cosmos(source_root),
        "dgm4": lambda: _dgm4(source_root),
        "meir": lambda: _meir(source_root, max_text_length),
        "mmfakebench": lambda: _mmfakebench(source_root),
        "newsclippings": lambda: _newsclippings(source_root),
        "verite": lambda: _verite(source_root),
    }
    if normalized not in readers:
        raise ValueError(f"unsupported multimodal source: {name}")
    if not source_root.is_dir():
        raise FileNotFoundError(f"source root not found: {source_root}")
    records = list(readers[normalized]())
    # Preserve source order but make accidental identical rows visible as one candidate.
    unique: dict[str, PairRecord] = {}
    for record in records:
        digest = hashlib.sha256(
            f"{record.image_path}\0{record.text}\0{record.label}".encode("utf-8")
        ).hexdigest()
        unique.setdefault(digest, record)
    return list(unique.values())
