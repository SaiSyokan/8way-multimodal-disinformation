import unittest
import json
import sys
import types
import tempfile
from pathlib import Path
from unittest.mock import patch

from octantfake_www.builder.pipeline import _supplement, build_dataset
from octantfake_www.records import ImageRecord, PairRecord, TextRecord


class AcceptingMismatchGate:
    def accepts(self, image_path, text, consistency):
        return consistency == "F", 0.1


class AcceptingGate:
    def accepts(self, image_path, text, consistency):
        return True, 0.5 if consistency == "T" else 0.1


class BuilderTests(unittest.TestCase):
    def test_only_missing_classes_can_be_supplemented(self):
        image = ImageRecord("image", "unused.jpg", "images", "T")
        text = TextRecord("text", "false text", "texts", "F")
        import random

        rows = _supplement(
            "TFF", 1, [image], [text], AcceptingMismatchGate(), set(), set(),
            random.Random(1), 10,
        )
        self.assertEqual(rows[0].label, "TFF")
        with self.assertRaises(ValueError):
            _supplement(
                "TFT", 1, [image], [text], AcceptingMismatchGate(), set(), set(),
                random.Random(1), 10,
            )

    def test_uniqueness_is_updated(self):
        images = [ImageRecord("image", "unused.jpg", "images", "F")]
        texts = [TextRecord("text", "false text", "texts", "F")]
        used_images = set()
        used_texts = set()
        import random

        rows = _supplement(
            "FFF", 2, images, texts, AcceptingMismatchGate(), used_images, used_texts,
            random.Random(1), 2,
        )
        self.assertEqual(len(rows), 1)
        self.assertEqual(len(used_images), 1)
        self.assertEqual(used_texts, {"false text"})

    def test_complete_balanced_build_has_portable_paths(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            media = root / "data"
            media.mkdir()
            direct = []
            for index, label in enumerate(("TTT", "TTF", "TFT", "FTT", "FTF", "FFT")):
                image = media / f"direct-{index}.jpg"
                image.write_bytes(b"synthetic")
                direct.append(
                    PairRecord(
                        sample_id=f"direct-{index}",
                        image_id=f"direct-image-{index}",
                        image_path=str(image),
                        text_id=f"direct-text-{index}",
                        text=f"direct text {index}",
                        image_veracity=label[0],
                        text_veracity=label[1],
                        image_text_consistency=label[2],
                        image_source="synthetic",
                        text_source="synthetic",
                    )
                )
            true_image = media / "true-pool.jpg"
            false_image = media / "false-pool.jpg"
            true_image.write_bytes(b"synthetic")
            false_image.write_bytes(b"synthetic")
            images = [
                ImageRecord("pool-image-t", str(true_image), "pool", "T"),
                ImageRecord("pool-image-f", str(false_image), "pool", "F"),
            ]
            texts = [
                TextRecord("pool-text-f1", "false pool text one", "pool", "F"),
                TextRecord("pool-text-f2", "false pool text two", "pool", "F"),
            ]
            config = {
                "seed": 2,
                "class_quota": 1,
                "calibration_size": 0,
                "test_size": 8,
                "media_root": "data",
                "clip": {"match_threshold": 0.32, "mismatch_threshold": 0.22},
                "multimodal_sources": {"synthetic": "data"},
                "single_modality_pools": {"images": "images.jsonl", "texts": "texts.jsonl"},
                "output_root": "release",
            }
            config_path = root / "config.yaml"
            config_path.write_text(json.dumps(config), encoding="utf-8")
            fake_yaml = types.SimpleNamespace(safe_load=json.loads)
            with patch.dict(sys.modules, {"yaml": fake_yaml}), patch(
                "octantfake_www.builder.pipeline.load_multimodal_source", return_value=direct
            ), patch(
                "octantfake_www.builder.pipeline.load_image_pool", return_value=images
            ), patch(
                "octantfake_www.builder.pipeline.load_text_pool", return_value=texts
            ):
                summary = build_dataset(config_path, gate=AcceptingGate())
            self.assertEqual(summary["total"], 8)
            rows = [json.loads(line) for line in (root / "release" / "octantfake.jsonl").read_text().splitlines()]
            self.assertTrue(all(not Path(row["image_path"]).is_absolute() for row in rows))
            self.assertEqual({row["label"] for row in rows}, {"TTT", "TTF", "TFT", "TFF", "FTT", "FTF", "FFT", "FFF"})


if __name__ == "__main__":
    unittest.main()
