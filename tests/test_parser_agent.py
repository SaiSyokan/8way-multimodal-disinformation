import tempfile
import unittest
from pathlib import Path

from octantfake_www.evidence.store import EvidenceStore
from octantfake_www.method.parser import parse_factor, parse_label
from octantfake_www.method.pipeline import OctantAgent


class FakeBackend:
    def generate(self, prompt, image_path=None):
        if "Describe only visible" in prompt:
            return "A synthetic scene."
        if "Describe the main event" in prompt:
            return "The same synthetic scene."
        if "verify the factual integrity of an image" in prompt:
            return '{"decision":"T","confidence":0.8,"explanation":"no contradiction"}'
        if "verify the factual integrity of the supplied text" in prompt:
            return '{"decision":"F","confidence":0.9,"explanation":"contradicted"}'
        if "Decide whether the image and text" in prompt:
            return '{"decision":"F","confidence":0.7,"explanation":"different contexts"}'
        if "Map the three ordered decisions" in prompt:
            return '{"label":"TFF","confidence":0.8,"explanation":"combined checks"}'
        raise AssertionError("unexpected prompt")


class ParserAgentTests(unittest.TestCase):
    def test_json_parsers(self):
        factor = parse_factor('prefix {"decision":"F","confidence":0.5,"explanation":"x"} suffix')
        self.assertEqual(factor.decision, "F")
        self.assertEqual(parse_label('{"label":"FFT","confidence":1,"explanation":"x"}')[0], "FFT")

    def test_malformed_does_not_fallback(self):
        with self.assertRaises(ValueError):
            parse_label("TTT maybe")

    def test_agent_checks_and_aggregates(self):
        with tempfile.TemporaryDirectory() as directory:
            result = OctantAgent(FakeBackend(), EvidenceStore(directory)).predict(
                {"sample_id": "synthetic", "image_path": "unused.jpg", "text": "claim"}
            )
            self.assertEqual(result.prediction, "TFF")
            self.assertIsNone(result.error)


if __name__ == "__main__":
    unittest.main()
