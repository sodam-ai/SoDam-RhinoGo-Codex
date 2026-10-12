import subprocess
import tempfile
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from generate_rhino7_model import DEFAULTS, build, validate
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

    def test_rejects_nonfinite_dimension_values(self):
        for key, value in (("length_mm", float("nan")), ("width_mm", float("inf")),
                           ("eave_height_mm", float("-inf")), ("footing_size_mm", True)):
            with self.subTest(key=key, value=value):
                with self.assertRaises(ValueError):
                    validate({**DEFAULTS, key: value})

    def test_invalid_parameters_rejected(self):
        with self.assertRaises(ValueError):
            build({**DEFAULTS, "frame_count": 1})

    def test_rejects_excessive_workload_and_coordinates(self):
        for key, value in (("frame_count", 1000000000),
                           ("roof_slat_count", 1000000000),
                           ("length_mm", 1e308)):
            with self.subTest(key=key):
                with self.assertRaises(ValueError):
                    validate({**DEFAULTS, key: value})

    def test_existing_sidecar_reports_are_preserved(self):
        scripts = Path(__file__).resolve().parents[1] / "scripts"
        with tempfile.TemporaryDirectory() as tmp:
            model_path = Path(tmp) / "model.3dm"
            build_report = model_path.with_suffix(".build.json")
            build_report.write_text("sentinel-build", encoding="utf-8")
            result = subprocess.run([sys.executable, str(scripts / "generate_rhino7_model.py"),
                                     str(model_path)], capture_output=True, text=True, check=False)
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse(model_path.exists())
            self.assertEqual(build_report.read_text(encoding="utf-8"), "sentinel-build")
            self.assertTrue(build(DEFAULTS.copy())[0].Write(str(model_path), 7))
            audit_report = model_path.with_suffix(".audit.json")
            audit_report.write_text("sentinel-audit", encoding="utf-8")
            result = subprocess.run([sys.executable, str(scripts / "inspect_rhino7_model.py"),
                                     str(model_path)], capture_output=True, text=True, check=False)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(audit_report.read_text(encoding="utf-8"), "sentinel-audit")


if __name__ == "__main__":
    unittest.main()
