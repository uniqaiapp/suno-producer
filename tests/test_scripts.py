"""Each script answers --help with exit 0, and every example in examples/manifest.json
reproduces its committed output byte for byte (this is how README numbers stay honest)."""
import json
import os
import subprocess
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = ["lyric_meter.py", "suno_lint.py", "brief.py"]


def run(args):
    return subprocess.run([sys.executable] + args, cwd=ROOT, capture_output=True, text=True, timeout=30)


class Help(unittest.TestCase):
    def test_help_exits_zero(self):
        for s in SCRIPTS:
            r = run([os.path.join("scripts", s), "--help"])
            self.assertEqual(r.returncode, 0, s)
            self.assertIn("usage:", r.stdout, s)

    def test_version_matches_skill(self):
        with open(os.path.join(ROOT, "SKILL.md"), encoding="utf-8") as fh:
            head = fh.read().split("---")[1]
        version = [ln.split(":", 1)[1].strip() for ln in head.splitlines() if ln.strip().startswith("version:")][0]
        for s in SCRIPTS:
            r = run([os.path.join("scripts", s), "--version"])
            self.assertEqual(r.stdout.strip(), version, s)


class Examples(unittest.TestCase):
    def test_manifest_reproduces(self):
        with open(os.path.join(ROOT, "examples", "manifest.json"), encoding="utf-8") as fh:
            manifest = json.load(fh)
        self.assertGreaterEqual(len(manifest), 5)
        for ex in manifest:
            r = run(ex["args"])
            self.assertEqual(r.returncode, ex.get("exit", 0), ex["output"] + "\n" + r.stderr)
            with open(os.path.join(ROOT, ex["output"]), encoding="utf-8") as fh:
                expected = fh.read()
            self.assertEqual(r.stdout, expected, ex["output"])


if __name__ == "__main__":
    unittest.main()
