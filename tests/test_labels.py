import unittest

from octantfake_www.labels import LABELS, from_legacy_label, label_from_factors, parse_label


class LabelTests(unittest.TestCase):
    def test_all_labels_round_trip(self):
        for label in LABELS:
            self.assertEqual(label_from_factors(*parse_label(label)), label)

    def test_legacy_notation(self):
        self.assertEqual(from_legacy_label("TTM"), "TTT")
        self.assertEqual(from_legacy_label("FFX"), "FFF")

    def test_invalid_factor_fails(self):
        with self.assertRaises(ValueError):
            label_from_factors("unknown", "T", "T")


if __name__ == "__main__":
    unittest.main()
