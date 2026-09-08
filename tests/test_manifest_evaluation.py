import json
import tempfile
import unittest
from pathlib import Path

from octantfake_www.evaluation import evaluate_predictions
from octantfake_www.manifest import validate_manifest


def write_jsonl(path, rows):
    path.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")


class ManifestEvaluationTests(unittest.TestCase):
    def test_valid_manifest_and_reuse_detection(self):
        row = {
            "sample_id": "one",
            "image_id": "image-one",
            "image_path": "not-distributed.jpg",
            "text_id": "text-one",
            "text": "Synthetic text",
            "image_veracity": "T",
            "text_veracity": "T",
            "image_text_consistency": "T",
            "label": "TTT",
            "image_source": "synthetic",
            "text_source": "synthetic",
            "construction_type": "test",
            "split": "calibration",
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "manifest.jsonl"
            write_jsonl(path, [row])
            self.assertTrue(validate_manifest(path)["valid"])
            duplicate = {**row, "sample_id": "two", "text_id": "text-two"}
            write_jsonl(path, [row, duplicate])
            result = validate_manifest(path)
            self.assertFalse(result["valid"])
            self.assertTrue(any("reused image_id" in error for error in result["errors"]))

    def test_invalid_prediction_is_incorrect_not_ttt(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "predictions.jsonl"
            write_jsonl(
                path,
                [
                    {"sample_id": "one", "gold_label": "TTT", "prediction": None},
                    {"sample_id": "two", "gold_label": "FFF", "prediction": "FFF"},
                ],
            )
            result = evaluate_predictions(path)
            self.assertEqual(result["invalid_predictions"], 1)
            self.assertEqual(result["correct"], 1)
            self.assertEqual(result["per_class"]["TTT"]["recall"], 0.0)

    def test_path_traversal_sample_id_is_rejected(self):
        row = {
            "sample_id": "../../outside",
            "image_id": "image-one",
            "image_path": "image.jpg",
            "text_id": "text-one",
            "text": "Synthetic text",
            "image_veracity": "T",
            "text_veracity": "T",
            "image_text_consistency": "T",
            "label": "TTT",
            "image_source": "synthetic",
            "text_source": "synthetic",
            "construction_type": "test",
            "split": "test",
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "manifest.jsonl"
            write_jsonl(path, [row])
            self.assertFalse(validate_manifest(path)["valid"])

    def test_repeated_content_is_reported_without_invalidating_frozen_release(self):
        row = {
            "sample_id": "one",
            "image_id": "image-one",
            "image_path": "one.jpg",
            "image_sha256": "a" * 64,
            "text_id": "text-one",
            "text": "Repeated text",
            "image_veracity": "T",
            "text_veracity": "T",
            "image_text_consistency": "T",
            "label": "TTT",
            "image_source": "synthetic",
            "text_source": "synthetic",
            "construction_type": "test",
            "split": "calibration",
        }
        duplicate = {
            **row,
            "sample_id": "two",
            "image_id": "image-two",
            "image_path": "two.jpg",
            "text_id": "text-two",
            "split": "test",
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "manifest.jsonl"
            write_jsonl(path, [row, duplicate])
            result = validate_manifest(path)
            self.assertTrue(result["valid"])
            self.assertEqual(len(result["warnings"]), 2)


if __name__ == "__main__":
    unittest.main()
