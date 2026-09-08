"""Canonical image/text/consistency labels."""

from __future__ import annotations

LABELS = ("TTT", "TTF", "TFT", "TFF", "FTT", "FTF", "FFT", "FFF")
FACTOR_VALUES = frozenset({"T", "F"})


def normalize_factor(value: object, name: str) -> str:
    factor = str(value).strip().upper()
    if factor not in FACTOR_VALUES:
        raise ValueError(f"{name} must be T or F; received {value!r}")
    return factor


def label_from_factors(image: object, text: object, consistency: object) -> str:
    """Encode factors in image/text/consistency order."""

    return "".join(
        (
            normalize_factor(image, "image_veracity"),
            normalize_factor(text, "text_veracity"),
            normalize_factor(consistency, "image_text_consistency"),
        )
    )


def parse_label(label: object) -> tuple[str, str, str]:
    normalized = str(label).strip().upper()
    if normalized not in LABELS:
        raise ValueError(f"label must be one of {', '.join(LABELS)}; received {label!r}")
    return normalized[0], normalized[1], normalized[2]


def from_legacy_label(label: object) -> str:
    """Convert historical M/X consistency notation to the paper notation."""

    normalized = str(label).strip().upper()
    if len(normalized) != 3 or normalized[:2] not in {"TT", "TF", "FT", "FF"}:
        raise ValueError(f"invalid legacy label: {label!r}")
    suffix = {"M": "T", "X": "F", "T": "T", "F": "F"}.get(normalized[2])
    if suffix is None:
        raise ValueError(f"invalid consistency suffix in {label!r}")
    return normalized[:2] + suffix

