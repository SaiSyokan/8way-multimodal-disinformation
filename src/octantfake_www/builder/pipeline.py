"""Deterministic, paper-aligned OctantFake construction pipeline."""

from __future__ import annotations

import random
from collections import Counter, defaultdict, deque
from pathlib import Path
from typing import Any, Iterable, Protocol

from ..io import dump_json, dump_jsonl
from ..labels import LABELS
from ..records import ImageRecord, PairRecord, TextRecord
from .clip_gate import ClipGate
from .mappers import load_multimodal_source
from .pools import load_image_pool, load_text_pool


class Gate(Protocol):
    def accepts(self, image_path: str, text: str, consistency: str) -> tuple[bool, float]: ...


def _image_key(path: str) -> str:
    return str(Path(path).expanduser().resolve())


def _text_key(text: str) -> str:
    return " ".join(text.casefold().split())


def _round_robin(candidates: Iterable[PairRecord], rng: random.Random) -> list[PairRecord]:
    by_source: dict[str, list[PairRecord]] = defaultdict(list)
    for record in candidates:
        by_source[record.image_source].append(record)
    queues: list[deque[PairRecord]] = []
    for source in sorted(by_source):
        rows = by_source[source]
        rng.shuffle(rows)
        queues.append(deque(rows))
    result: list[PairRecord] = []
    while queues:
        remaining: list[deque[PairRecord]] = []
        for queue in queues:
            result.append(queue.popleft())
            if queue:
                remaining.append(queue)
        queues = remaining
    return result


def _take_direct(
    candidates: list[PairRecord],
    quota: int,
    gate: Gate,
    used_images: set[str],
    used_texts: set[str],
    rng: random.Random,
) -> list[PairRecord]:
    selected: list[PairRecord] = []
    for record in _round_robin(candidates, rng):
        if len(selected) >= quota:
            break
        image_key = _image_key(record.image_path)
        text_key = _text_key(record.text)
        if image_key in used_images or text_key in used_texts:
            continue
        accepted, similarity = gate.accepts(
            record.image_path, record.text, record.image_text_consistency
        )
        if not accepted:
            continue
        selected.append(
            PairRecord(**{
                **{key: value for key, value in record.__dict__.items() if key != "metadata"},
                "metadata": {**record.metadata, "clip_similarity": similarity},
            })
        )
        used_images.add(image_key)
        used_texts.add(text_key)
    return selected


def _supplement(
    label: str,
    amount: int,
    images: list[ImageRecord],
    texts: list[TextRecord],
    gate: Gate,
    used_images: set[str],
    used_texts: set[str],
    rng: random.Random,
    max_attempts_per_sample: int,
) -> list[PairRecord]:
    if label not in {"TFF", "FFF"}:
        raise ValueError(f"single-modality supplementation is not allowed for {label}")
    image_factor, text_factor, consistency = label
    image_candidates = [row for row in images if row.veracity == image_factor]
    text_candidates = [row for row in texts if row.veracity == text_factor]
    rng.shuffle(image_candidates)
    rng.shuffle(text_candidates)
    selected: list[PairRecord] = []
    image_cursor = 0
    text_cursor = 0
    attempts = 0
    attempt_limit = max(amount * max_attempts_per_sample, amount)

    while len(selected) < amount and attempts < attempt_limit:
        attempts += 1
        if not image_candidates or not text_candidates:
            break
        image = image_candidates[image_cursor % len(image_candidates)]
        text = text_candidates[text_cursor % len(text_candidates)]
        image_cursor += 1
        text_cursor += 7  # coprime stride reduces repeated source combinations
        image_key = _image_key(image.path)
        text_key = _text_key(text.text)
        if image_key in used_images or text_key in used_texts:
            continue
        accepted, similarity = gate.accepts(image.path, text.text, consistency)
        if not accepted:
            # Keep the image available for a different text and advance asymmetrically.
            text_cursor += 1
            continue
        sample_index = len(selected)
        selected.append(
            PairRecord(
                sample_id=f"supplement-{label.lower()}-{sample_index:07d}",
                image_id=image.source_id,
                image_path=image.path,
                text_id=text.source_id,
                text=text.text,
                image_veracity=image_factor,
                text_veracity=text_factor,
                image_text_consistency=consistency,
                image_source=image.source,
                text_source=text.source,
                construction_type="cross_modal_supplement",
                metadata={
                    "clip_similarity": similarity,
                    "image_metadata": dict(image.metadata),
                    "text_metadata": dict(text.metadata),
                },
            )
        )
        used_images.add(image_key)
        used_texts.add(text_key)
    return selected


def _assign_splits(
    records: list[PairRecord], calibration_size: int, test_size: int, seed: int
) -> list[PairRecord]:
    rng = random.Random(seed)
    if len(records) != calibration_size + test_size:
        raise RuntimeError(
            f"expected {calibration_size + test_size} records, found {len(records)}"
        )
    shuffled = list(records)
    rng.shuffle(shuffled)
    return [
        PairRecord(
            **{
                **row.__dict__,
                "split": "calibration" if index < calibration_size else "test",
            }
        )
        for index, row in enumerate(shuffled)
    ]


def _portable_paths(records: list[PairRecord], media_root: Path) -> list[PairRecord]:
    portable: list[PairRecord] = []
    resolved_root = media_root.expanduser().resolve()
    for row in records:
        try:
            relative = Path(row.image_path).expanduser().resolve().relative_to(resolved_root)
        except ValueError as exc:
            raise ValueError(
                f"image is outside configured media_root and cannot be exported portably: {row.image_path}"
            ) from exc
        portable.append(PairRecord(**{**row.__dict__, "image_path": relative.as_posix()}))
    return portable


def build_dataset(config_path: str | Path, gate: Gate | None = None) -> dict[str, Any]:
    """Build manifests from a YAML configuration and return an audit summary."""

    try:
        import yaml
    except ImportError as exc:
        raise RuntimeError("Install the package before building: pip install -e .") from exc
    config_file = Path(config_path).expanduser().resolve()
    config = yaml.safe_load(config_file.read_text(encoding="utf-8")) or {}
    seed = int(config.get("seed", 2026))
    rng = random.Random(seed)
    quota = int(config.get("class_quota", 1100))
    calibration = int(config.get("calibration_size", 800))
    test = int(config.get("test_size", 8000))
    if quota * len(LABELS) != calibration + test:
        raise ValueError("8 * class_quota must equal calibration_size + test_size")

    thresholds = config.get("clip", {})
    if float(thresholds.get("match_threshold", 0.32)) != 0.32:
        raise ValueError("the paper-aligned match_threshold is fixed at 0.32")
    if float(thresholds.get("mismatch_threshold", 0.22)) != 0.22:
        raise ValueError("the paper-aligned mismatch_threshold is fixed at 0.22")
    active_gate = gate or ClipGate(
        model_name=str(thresholds.get("model", "openai/clip-vit-base-patch32")),
        device=thresholds.get("device"),
        match_threshold=0.32,
        mismatch_threshold=0.22,
    )

    def resolve(value: str) -> Path:
        path = Path(value).expanduser()
        return path if path.is_absolute() else (config_file.parent / path).resolve()

    direct: list[PairRecord] = []
    for name, root in (config.get("multimodal_sources") or {}).items():
        direct.extend(
            load_multimodal_source(
                str(name), resolve(str(root)), int(config.get("meir_max_text_length", 160))
            )
        )

    image_pool = load_image_pool(resolve(str(config["single_modality_pools"]["images"])))
    text_pool = load_text_pool(resolve(str(config["single_modality_pools"]["texts"])))
    used_images: set[str] = set()
    used_texts: set[str] = set()
    selected: list[PairRecord] = []
    for label in LABELS:
        rows = _take_direct(
            [row for row in direct if row.label == label],
            quota, active_gate, used_images, used_texts, rng,
        )
        shortfall = quota - len(rows)
        if shortfall and label in {"TFF", "FFF"}:
            rows.extend(
                _supplement(
                    label, shortfall, image_pool, text_pool, active_gate,
                    used_images, used_texts, rng,
                    int(config.get("max_attempts_per_sample", 500)),
                )
            )
        if len(rows) != quota:
            raise RuntimeError(
                f"{label}: selected {len(rows)}/{quota}; add eligible source candidates or review paths"
            )
        selected.extend(rows)

    final = _assign_splits(selected, calibration, test, seed)
    if "media_root" not in config:
        raise ValueError("media_root is required so manifests never contain machine-specific paths")
    final = _portable_paths(final, resolve(str(config["media_root"])))
    output_root = resolve(str(config.get("output_root", "../release")))
    dump_jsonl(output_root / "octantfake.jsonl", (row.to_dict() for row in final))
    dump_jsonl(
        output_root / "calibration.jsonl",
        (row.to_dict() for row in final if row.split == "calibration"),
    )
    dump_jsonl(
        output_root / "test.jsonl",
        (row.to_dict() for row in final if row.split == "test"),
    )
    summary = {
        "seed": seed,
        "total": len(final),
        "labels": dict(sorted(Counter(row.label for row in final).items())),
        "splits": dict(sorted(Counter(row.split for row in final).items())),
        "construction_types": dict(sorted(Counter(row.construction_type for row in final).items())),
        "unique_images": len({row.image_id for row in final}),
        "unique_texts": len({row.text_id for row in final}),
    }
    dump_json(output_root / "build_summary.json", summary)
    return summary
