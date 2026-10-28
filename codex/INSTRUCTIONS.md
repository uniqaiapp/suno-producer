# suno-producer for Codex

Paste the block below into your project's AGENTS.md (or Codex custom instructions),
and copy `SKILL.md`, `scripts/` and `references/` from https://github.com/uniqaiapp/suno-producer into `.agents/skills/suno-producer/`.

---
When the user asks for a Suno prompt, Suno style tags or meta-tags, a song structure, lyrics for Suno, or an A/B variant of a song (in English or Russian; "напиши песню для Suno", "промпт для Suno"), follow `.agents/skills/suno-producer/SKILL.md`. Run `python3 .agents/skills/suno-producer/scripts/suno_lint.py` and `lyric_meter.py` on the result before handing it back.
---
