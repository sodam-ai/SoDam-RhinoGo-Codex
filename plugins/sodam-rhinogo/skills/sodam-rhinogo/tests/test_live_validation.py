import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "assets"))
from sodam_rhinogo_parameters import DEFAULTS, validate_parameters


class LiveParameterValidationTests(unittest.TestCase):
    def test_valid_boundaries_and_default(self):
        validate_parameters(DEFAULTS.copy())
        validate_parameters({**DEFAULTS, "frame_count": 2, "louver_count_per_side": 1})

    def test_rejects_nonfinite_and_nonnumeric_values(self):
        cases = [
            ("length", float("nan")), ("width", float("inf")),
            ("ridge_height", float("-inf")), ("entrance_width", True),
            ("column_section", [200, float("nan")]),
            ("beam_section", "200,300"),
            ("louver_angle_deg", float("nan")),
            ("entrance_offset", "200"),
            ("frame_count", True), ("louver_count_per_side", False),
        ]
        for key, value in cases:
            with self.subTest(key=key, value=value), self.assertRaises(ValueError):
                validate_parameters({**DEFAULTS, key: value})

    def test_rejects_excessive_or_degenerate_geometry(self):
        cases = [
            ("frame_count", 1000000000),
            ("louver_count_per_side", 1000000000),
            ("length", 100),
            ("eave_height", 100),
            ("width", 300),
            ("louver_angle_deg", 1e308),
            ("ridge_height", 1e308),
        ]
        for key, value in cases:
            with self.subTest(key=key, value=value), self.assertRaises(ValueError):
                validate_parameters({**DEFAULTS, key: value})

    @unittest.skipUnless(shutil.which("pwsh") and Path(r"C:\Program Files\Rhino 7\System\Rhino.exe").exists(),
                         "PowerShell and Rhino 7 are needed for launcher preflight")
    def test_launcher_preserves_existing_sidecar(self):
        launcher = Path(__file__).resolve().parents[1] / "scripts" / "launch_rhino7_live.ps1"
        with tempfile.TemporaryDirectory() as tmp:
            model = Path(tmp) / "model.3dm"
            report = model.with_suffix(".audit.json")
            report.write_text("sentinel-audit", encoding="utf-8")
            result = subprocess.run(["pwsh", "-NoProfile", "-File", str(launcher),
                                     "-OutputFile", str(model), "-TimeoutSeconds", "1"],
                                    capture_output=True, text=True, encoding="utf-8",
                                    errors="replace", check=False)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Preserving existing report", result.stderr)
            self.assertFalse(model.exists())
            self.assertEqual(report.read_text(encoding="utf-8"), "sentinel-audit")

    def test_launcher_preflight_cli(self):
        validator = Path(__file__).resolve().parents[1] / "scripts" / "validate_live_rhino7_params.py"
        good = subprocess.run([sys.executable, str(validator)], capture_output=True, text=True, check=False)
        self.assertEqual(good.returncode, 0, good.stderr)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "params.json"
            for name, content in (
                ("valid_boundary", '{"frame_count":2,"louver_count_per_side":1}'),
                ("invalid_count", '{"frame_count":1}'),
                ("nonfinite", '{"length":NaN}'),
                ("unknown_key", '{"not_a_parameter":1}'),
                ("malformed_json", '{"frame_count":'),
                ("excessive_count", '{"frame_count":1000000000}'),
                ("short_eave", '{"eave_height":100}'),
            ):
                with self.subTest(name=name):
                    path.write_text(content, encoding="utf-8")
                    result = subprocess.run([sys.executable, str(validator), "--parameters", str(path)],
                                            capture_output=True, text=True, check=False)
                    self.assertEqual(result.returncode, 0 if name == "valid_boundary" else 2,
                                     result.stderr)


if __name__ == "__main__":
    unittest.main()
