# Changelog

All notable changes to this project are documented here. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses [Semantic Versioning](https://semver.org/).

## [0.1.0] - 2026-10-28

### Added

- `SKILL.md`: the Suno producer skill (brief → style prompt → structure → lyrics → checks → delivery), with Claude Code, Cursor and Codex adapters.
- `scripts/brief.py`: style prompt with one-axis A/B/C variants, section structure and lyric brief from `references/genres.json` (23 genres, 7 moods, 5 vocal types, 8 structures).
- `scripts/lyric_meter.py`: syllable counter (English heuristic, Russian vowel count), rhyme scheme per section with full/slant marking, drift warnings, JSON output.
- `scripts/suno_lint.py`: 16 lint rules (`L001`–`L016`) for tags, structure, budgets and artist-imitation phrases in lyrics and style prompts.
- References: section tags, style prompt vocabulary and artist-to-sound translation, lyric craft, Russian vocals (in Russian), A/B testing, troubleshooting.
- Examples: an English synthwave/indie-pop song, a Russian rock ballad, a deliberately broken file, and committed outputs reproduced by the tests.
- Tests (`python3 tests/run.py`): meter, lint, brief data and determinism, script help/version, byte-for-byte example reproduction, adapter consistency and forbidden strings.
- Animated README banner, terminal demo and social preview from the shared uniqaiapp design kit.
