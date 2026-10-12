import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "compare_model_metrics.py"


class CompareModelMetricsTests(unittest.TestCase):
    def test_comparison_expectations_and_new_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            before, after, report = (root / name for name in ("before.json", "after.json", "report.json"))
            before.write_text(json.dumps({"objects": 41, "units": "mm"}), encoding="utf-8")
            after.write_text(json.dumps({"objects": 67, "units": "mm"}), encoding="utf-8")
            result = subprocess.run([sys.executable, str(SCRIPT), str(before), str(after),
                                     "--expect-change", "objects", "--expect-same", "units",
                                     "--output", str(report)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(json.loads(report.read_text(encoding="utf-8"))["expectations_pass"])

    def test_existing_report_is_preserved(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            before, after, report = (root / name for name in ("before.json", "after.json", "report.json"))
            before.write_text('{"objects":41}', encoding="utf-8")
            after.write_text('{"objects":67}', encoding="utf-8")
            report.write_text("sentinel-preserve", encoding="utf-8")
            result = subprocess.run([sys.executable, str(SCRIPT), str(before), str(after),
                                     "--output", str(report)], capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(report.read_text(encoding="utf-8"), "sentinel-preserve")

    def test_invalid_tolerance_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            before, after = (root / name for name in ("before.json", "after.json"))
            before.write_text("{}", encoding="utf-8")
            after.write_text("{}", encoding="utf-8")
            for tolerance in ("-1", "nan", "inf"):
                with self.subTest(tolerance=tolerance):
                    result = subprocess.run([sys.executable, str(SCRIPT), str(before), str(after),
                                             "--tolerance", tolerance], capture_output=True, text=True)
                    self.assertEqual(result.returncode, 2, result.stderr)


if __name__ == "__main__":
    unittest.main()
