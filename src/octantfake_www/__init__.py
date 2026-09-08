"""OctantFake and OctantAgent utilities for the WWW'26 release."""

from .labels import LABELS, label_from_factors, parse_label
from .records import FactorResult, PairRecord, PredictionRecord

__all__ = [
    "LABELS",
    "FactorResult",
    "PairRecord",
    "PredictionRecord",
    "label_from_factors",
    "parse_label",
]

__version__ = "1.0.0"

