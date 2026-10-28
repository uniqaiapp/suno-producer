#!/usr/bin/env python3
"""Regenerate every committed output in examples/outputs/ from examples/manifest.json.

    python3 examples/regen.py

Run it after changing a script or an example input, then review the diff. tests/test_scripts.py
checks that the committed outputs match what the scripts print today.
"""
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    with open(os.path.join(ROOT, "examples", "manifest.json"), encoding="utf-8") as fh:
        manifest = json.load(fh)
    os.makedirs(os.path.join(ROOT, "examples", "outputs"), exist_ok=True)
    for ex in manifest:
        r = subprocess.run([sys.executable] + ex["args"], cwd=ROOT, capture_output=True, text=True)
        if r.returncode != ex.get("exit", 0):
            print("unexpected exit %d for %s\n%s" % (r.returncode, " ".join(ex["args"]), r.stderr))
            return 1
        with open(os.path.join(ROOT, ex["output"]), "w", encoding="utf-8") as fh:
            fh.write(r.stdout)
        print("wrote %s (%d bytes)" % (ex["output"], len(r.stdout.encode("utf-8"))))
    return 0


if __name__ == "__main__":
    sys.exit(main())
