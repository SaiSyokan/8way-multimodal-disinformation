import json
import tempfile
import unittest
from pathlib import Path

from octantfake_www.builder.mappers import load_multimodal_source


class MapperTests(unittest.TestCase):
    def test_dgm4_unknown_class_is_excluded(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "metadata").mkdir()
            (root / "origin").mkdir()
            (root / "origin" / "known.jpg").write_bytes(b"synthetic")
            (root / "origin" / "unknown.jpg").write_bytes(b"synthetic")
            rows = [
                {
                    "image": "DGM4/origin/known.jpg",
                    "text": "Known mapping",
                    "fake_cls": "text_swap",
                },
                {
                    "image": "DGM4/origin/unknown.jpg",
                    "text": "Must not become TTT",
                    "fake_cls": "future_unknown_class",
                },
            ]
            (root / "metadata" / "test.json").write_text(
                json.dumps(rows), encoding="utf-8"
            )
            mapped = load_multimodal_source("DGM4", root)
            self.assertEqual(len(mapped), 1)
            self.assertEqual(mapped[0].label, "TTF")


if __name__ == "__main__":
    unittest.main()
