# AGENTS.md

This repository is an agent skill. The full instructions are in `SKILL.md`; read it first.

## Working in this repo

- Zero dependencies: Python 3.9+ stdlib only. Do not add packages, lockfiles or vendored dependency directories.
- Run tests: `python3 tests/run.py`. Example outputs are regenerated with `python3 examples/regen.py` and must match byte for byte.
- Keep `SKILL.md` under 500 lines; long material goes to `references/`.
- `references/genres.json` is data for `scripts/brief.py`; `tests/test_brief.py` validates every genre block.
- Author and maintainer is UniqAI <support@uniqai.app>; do not add personal names anywhere.
- No copyrighted lyrics in examples or tests; no artist names in prompts.

## Using this skill from another project

Copy or clone this repo, then follow "Install" in README.md. When the user asks for a Suno prompt, Suno tags, song structure or lyrics for Suno (in English or Russian), follow `SKILL.md`.
