import tempfile
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from generate_rhino7_model import DEFAULTS, build
from inspect_rhino7_model import inspect


class OfflineRhino7Tests(unittest.TestCase):
    def test_saved_archive_is_rhino7_and_closed(self):
        model, summary = build(DEFAULTS.copy())
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.3dm"
            self.assertTrue(model.Write(str(path), 7))
            report = inspect(path)
        self.assertTrue(report["overall_pass"], report["issues"])
        self.assertEqual(report["archive_version"], 70)
        self.assertEqual(report["object_count"], summary["object_count"])
        self.assertEqual(report["counts"], summary["counts"])

    def test_parameter_change_propagates_into_saved_geometry(self):
        baseline = DEFAULTS.copy()
        changed = {**baseline, "length_mm": 15000.0, "frame_count": 7}
        with tempfile.TemporaryDirectory() as tmp:
            paths = [Path(tmp) / "base.3dm", Path(tmp) / "changed.3dm"]
            for params, path in zip((baseline, changed), paths):
                self.assertTrue(build(params)[0].Write(str(path), 7))
            reports = [inspect(path) for path in paths]
        self.assertTrue(all(report["overall_pass"] for report in reports))
        self.assertGreater(reports[1]["object_count"], reports[0]["object_count"])
        self.assertGreater(reports[1]["bbox"]["max"][0], reports[0]["bbox"]["max"][0])
        self.assertEqual(reports[1]["bbox"]["min"][1:], reports[0]["bbox"]["min"][1:])

    def test_invalid_parameters_rejected(self):
        with self.assertRaises(ValueError):
            build({**DEFAULTS, "frame_count": 1})


if __name__ == "__main__":
    unittest.main()
