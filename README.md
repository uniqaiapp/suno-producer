<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/banner.svg">
  <source media="(prefers-color-scheme: light)" srcset="assets/banner-light.svg">
  <img alt="suno-producer: Suno style prompts and lyrics structure that behave" src="assets/banner.svg" width="1280" height="320">
</picture>

[![License: MIT](https://img.shields.io/badge/license-MIT-d1fe17?style=flat-square&labelColor=0d0f12)](LICENSE)
[![Claude Code skill](https://img.shields.io/badge/Claude_Code-skill-d1fe17?style=flat-square&labelColor=0d0f12)](#install)
[![Cursor](https://img.shields.io/badge/Cursor-rules-d1fe17?style=flat-square&labelColor=0d0f12)](#install)
[![Codex](https://img.shields.io/badge/Codex-AGENTS.md-d1fe17?style=flat-square&labelColor=0d0f12)](#install)
[![Made by UniqAI](https://img.shields.io/badge/made_by-UniqAI-fdfc07?style=flat-square&labelColor=0d0f12)](https://uniqai.app/?utm_source=github&utm_medium=readme&utm_campaign=suno-producer)

**Suno prompts, meta-tags and lyric structure that the model actually follows, in English and Russian.**

[Quickstart](#quickstart) · [How it works](#how-it-works) · [Lint rules](#lint-rules) · [Examples](#examples) · [Install](#install) · [FAQ](#faq)

[Русская версия](README.ru.md)

</div>

# suno-producer: Suno prompts, meta-tags and lyric structure

Suno prompts in three parts: a one-line **style prompt** (genre, BPM, key, mood, instruments, production, vocal), a **section structure** with meta-tags (`[Intro]`, `[Verse]`, `[Pre-Chorus]`, `[Chorus]`, `[Drop]`, `[Bridge]`, `[Outro]`), and **lyrics** whose lines are even enough for a generated vocal to sing without rushing, written for the Style and Lyrics fields of the Suno editor. The tag list and field budgets were compiled against Suno v4.5 and later (v5.5 is the current model as of 2026-10, per [Suno's March 2026 release coverage](https://www.musicbusinessworldwide.com/suno-launches-v5-5-ai-model-with-voice-capture-and-personalization-features)); the editor shows the live limits, and the lint budgets are flags you can override. It runs as a Claude Code skill, a Cursor rule or a Codex `AGENTS.md` snippet, and the three scripts work on their own as a plain checklist with a lint. UniqAI makes photo, video and chat tools, not music; this is a side project we use ourselves.

| **Brief in, prompt out** | **Lyric meter, EN + RU** | **Lint before you spend credits** |
|:---|:---|:---|
| `brief.py` turns "sad synthwave, female vocal" into a style prompt, two one-axis A/B variants, a tagged structure and per-section syllable targets. | `lyric_meter.py` counts syllables per line, derives the rhyme scheme per section and flags lines that drift from the section median. English heuristics, exact Russian vowel counting. | `suno_lint.py` checks tag spelling and placement, structure order, section length, field budgets and artist-imitation phrases. Stable rule ids, exit code 1 on errors. |

## Quickstart

```bash
git clone https://github.com/uniqaiapp/suno-producer
cd suno-producer
python3 scripts/brief.py --genre synthwave --fuse "indie pop" --mood melancholic --seed 7
python3 scripts/lyric_meter.py examples/lyrics/midnight-bus.txt
python3 scripts/suno_lint.py examples/lyrics/bad-tags.txt --style examples/style/bad-style.txt
```

The first command prints a style prompt with variants B and C, a `[Intro] … [Outro]` structure and a lyric brief. The second prints syllables per line and the rhyme scheme of every section of the sample song. The third fails with three errors and nine warnings, each with a rule id and a line number. Python 3.9+, no packages to install.

## Demo

<img alt="suno-producer demo: lyric_meter reports syllables and rhyme scheme per section of the sample song, then suno_lint lists two errors and seven warnings with rule ids and line numbers on a deliberately broken file" src="assets/demo.svg" width="900">

## How it works

1. **Brief.** `scripts/brief.py` reads `references/genres.json` (tempo range, keys, instruments, production words and default vocal per genre; editorial defaults, not measurements) and assembles a comma-separated style prompt in the order the model weights: genre, fusion, tempo, key, two mood words, instruments, production, vocal, language. With `--fuse` it uses the overlap of the two tempo ranges. It also picks the section structure for the genre and prints lines-per-section and syllable budgets.

2. **Variants.** Each variant changes exactly one descriptor (vocal, production, or tempo by about 8 %), so an A/B listen tells you which change mattered. `tests/test_brief.py` asserts the one-descriptor difference. Output is deterministic for a `--seed`.

3. **Meter.** `scripts/lyric_meter.py` splits the lyrics by `[Section]` tag, counts syllables (English: vowel groups with silent-e, -ed, -es and -le rules; Russian: one vowel, one syllable), builds the rhyme scheme from word endings (uppercase = full rhyme, lowercase = slant), and warns when a line is more than two syllables from the section median. Whole-line `(backing vocals)` are exempt.

4. **Lint.** `scripts/suno_lint.py` walks the lyrics once and reports against the rule table below, then checks the style prompt for tags, artist phrases, line count, tempo and budget. `--json` for machines, `--strict` to fail on warnings.

5. **The skill** (`SKILL.md`) ties it together for an agent: clarify the brief, run `brief.py`, write the lyrics into the structure, run both checks, deliver Style + Lyrics + variants in a fixed format, and when the user comes back with a bad generation, change one thing from `references/troubleshooting.md`.

```
description ──► brief.py ──► style prompt A/B/C + structure + lyric brief
                                   │
                              write lyrics
                                   │
                 lyric_meter.py ◄──┴──► suno_lint.py
                 syllables, scheme       tags, order, budgets, L001–L016
                                   │
                           Style + Lyrics + variants
```

## Lint rules

| Id | Level | Check |
|---|---|---|
| L001 | warn | Tag not in the known list (`references/section-tags.md`); the model may sing it |
| L002 | warn | Lyrics before the first tag, or no tags at all |
| L003 | warn | No `[Chorus]`, `[Hook]` or `[Drop]` (skip with `--instrumental`) |
| L004 | warn | The same tag twice in a row |
| L005 | warn | `[Intro]` not first or `[Outro]` not last |
| L006 | error / warn | Unbalanced `[ ]` (error) or `( )` (warn) on a line |
| L007 | error | Artist-imitation phrase ("in the style of", "sounds like", "в стиле", "как у") in lyrics or style |
| L008 | error / warn | Style prompt over budget (`--max-style`, default 1000) / empty |
| L009 | error | Lyrics over budget (`--max-lyrics`, default 5000) |
| L010 | warn | A tag inside a lyric line |
| L011 | warn | Section longer than `--max-section-lines` (default 12) |
| L012 | warn | `[Tags]` in the style prompt |
| L013 | warn | Style prompt spread over more than three lines |
| L014 | warn | Lower-case tag |
| L015 | info | No tempo in the style prompt |
| L016 | warn | A lyric section with no lines (instrumental tags are exempt) |

The budgets are defaults, not a specification; the Suno editor shows the live limit next to each field.

## Examples

Every output below is committed under `examples/outputs/` and reproduced byte for byte by `python3 tests/run.py`; `examples/README.md` lists the commands.

<details>
<summary><b>Meter report for an English song (synthwave / indie pop)</b></summary>

Input: `examples/lyrics/midnight-bus.txt`. Command: `python3 scripts/lyric_meter.py examples/lyrics/midnight-bus.txt`.

```text
[Verse 1]      4 lines · syllables 6-8 · scheme ABAB
   1   6  Streetlights hum a tired song                A
   2   7  Rain keeps tapping on the glass              B
   3   8  Every stop takes twice as long               A
   4   7  Watching all the faces pass                  B
[Pre-Chorus]   2 lines · syllables 8-9 · scheme AA
   1   8  I count the stops, I count the miles         A
   2   9  I keep your seat warm for a while            A
[Chorus]       4 lines · syllables 6-9 · scheme AABB
   1   6  Midnight bus, take me home                   A
   2   7  Through a city made of chrome                A
   3   9  Every window's a telephone                   B
   4   7  Ringing nowhere, ringing on                  B
```

Full report: `examples/outputs/midnight-bus.meter.txt`. The song passes the lint clean with its style prompt `examples/style/midnight-bus.txt`.

</details>

<details>
<summary><b>Meter report for a Russian song (rock ballad)</b></summary>

Input: `examples/lyrics/severny-veter.ru.txt`. Command: `python3 scripts/lyric_meter.py examples/lyrics/severny-veter.ru.txt`.

```text
[Verse 1]      4 lines · syllables 10 · scheme AABB
   1  10  Северный ветер стучится в окно               A
   2  10  Чай на столе остывает давно                  A
   3  10  Я не ответил на тысячу слов                  B
   4  10  Город молчит, и молчать я готов              B
[Chorus]       4 lines · syllables 8 · scheme ABAB
   1   8  Не уходи, пока горит                         A
   2   8  Последний свет в моём окне                   B
   3   8  Пусть этот город говорит                     A
   4   8  О ком-то, но не обо мне                      B
```

Every rhyme here is full by the script's ending rule. For a slant rhyme, see verse 2 of the English song above: `scheme ABaB`, where lowercase `a` marks `door` / `for` as an ending-only match. Russian specifics: `references/russian-vocals.md`.

</details>

<details>
<summary><b>Lint on a deliberately broken file</b></summary>

Command: `python3 scripts/suno_lint.py examples/lyrics/bad-tags.txt --style examples/style/bad-style.txt` (exit code 1).

```text
! L002  lyrics before the first section tag; Suno treats untagged text as a verse
x L007  artist-imitation phrase in style prompt ("sounds like"); describe the sound instead
! L012  style prompt contains [tags]; tags belong in the lyrics field
! L014  line 2: tag [intro] is lower-case; write tags Capitalised for consistency
x L007  line 4: artist-imitation phrase in lyrics ("sound like"); Suno rejects named artists
! L016  line 5: section [Verse 1] has no lines
! L001  line 6: unknown tag [Guitar Shred]; Suno may sing it instead of following it
x L006  line 7: unbalanced square brackets
! L010  line 9: tag inside a lyric line; put each tag on its own line
! L011  line 10: [Chorus] has 13 lines (limit 12); long sections tend to get rushed or cut
! L005  line 24: [Outro] is not the last tag
= 3 error(s), 9 warning(s), 1 info
```

</details>

<details>
<summary><b>Brief with one-axis variants</b></summary>

Command: `python3 scripts/brief.py --genre synthwave --fuse "indie pop" --mood melancholic --seed 7`.

```text
Style prompt (paste into the Style field)
  A  [base] synthwave, indie pop, 108 BPM, C minor, melancholic, wistful, gated reverb drums, retro drum machine, jangly electric guitar, 80s production, lo-fi warmth, warm female vocal
  B  [vocal] … 80s production, lo-fi warmth, breathy female vocal
  C  [production] … jangly electric guitar, wide stereo pads, lo-fi warmth, warm female vocal

Structure (pop)
  [Intro] [Verse 1] [Pre-Chorus] [Chorus] [Verse 2] [Pre-Chorus] [Chorus] [Bridge] [Chorus] [Outro]
```

Full output (B and C unabridged, plus the lyric brief): `examples/outputs/brief-synthwave-indie-pop.txt`. Russian variant: `examples/outputs/brief-russian-rock.ru.txt`.

</details>

## Install

Works with every agent that reads instruction files. Pick yours. Requirements: Python 3.9+. No packages to install.

<details open>
<summary><b>Claude Code</b></summary>

```bash
# global
git clone https://github.com/uniqaiapp/suno-producer ~/.claude/skills/suno-producer
# or project-local
git clone https://github.com/uniqaiapp/suno-producer .claude/skills/suno-producer
# or via the skills CLI
npx skills add uniqaiapp/suno-producer
```

Then `/suno-producer` in any session, or just describe the song; the skill's `description` triggers it. As a plugin, once the uniqaiapp marketplace is published: `/plugin marketplace add uniqaiapp/skills` then `/plugin install suno-producer@uniqaiapp`.

</details>

<details>
<summary><b>Cursor</b></summary>

Copy `SKILL.md`, `scripts/`, `references/` and [`.cursor/rules/suno-producer.mdc`](.cursor/rules/suno-producer.mdc) into your project. The rule file embeds the skill.

</details>

<details>
<summary><b>Codex / any AGENTS.md agent</b></summary>

Copy `SKILL.md`, `scripts/` and `references/` into `.agents/skills/suno-producer/` and add the snippet from [`codex/INSTRUCTIONS.md`](codex/INSTRUCTIONS.md) to your `AGENTS.md`.

</details>

<details>
<summary><b>Plain prompt, or no agent at all</b></summary>

Paste [`SKILL.md`](SKILL.md) into the system prompt of any model; it has no agent-specific syntax outside the frontmatter. Every script runs standalone: `python3 scripts/<name>.py --help`.

</details>

## Limits and honesty

- Syllable counts are heuristics for English (usually within one of a dictionary count; "fire", "idea", "every" are typical misses) and exact vowel counts for Russian. Rhyme detection compares endings and knows nothing about stress.
- The scripts never call Suno. They remove the known causes of bad generations; they cannot promise a good one.
- Every number in this README (syllable counts, rule counts, `3 error(s), 9 warning(s)`) is the output of a script in this repo on a file in this repo, reproduced by the tests. The genre table's tempo ranges are editorial defaults, not measurements, and say so in the file.
- Not affiliated with Suno. No copyrighted lyrics are included or should be requested; the lint rejects "in the style of" an artist.

## Related

- [video-director](https://github.com/uniqaiapp/video-director): turn a one-line idea into a shot-by-shot prompt for AI video models (Kling, Veo, Sora and others), with camera, lighting and motion vocabulary.
- [deslop-ru](https://github.com/uniqaiapp/deslop-ru): strip AI-sounding filler from Russian text: a skill plus a stdlib script that flags and rewrites the usual tells.
- [token-diet](https://github.com/uniqaiapp/token-diet): cut prompt and context tokens without losing meaning: measurable rules, a stdlib estimator, and before/after examples.

## FAQ

<details>
<summary><b>Why does Suno sing the word "Chorus"?</b></summary>

The tag was not recognised as structure: misspelt, lower-case, or on the same line as lyrics. Put a known tag from `references/section-tags.md` on its own line, Capitalised. `suno_lint.py` flags all three cases (L001, L010, L014).

</details>

<details>
<summary><b>Can I ask for a song in the style of a specific artist?</b></summary>

No; Suno rejects artist names and the result would be an imitation. Translate what you hear into sound words (era, instruments, production, vocal). `references/style-prompts.md` has a table, and the lint flags the phrases (L007).

</details>

<details>
<summary><b>Does it work for Russian lyrics?</b></summary>

Yes. Syllable counting is exact for Russian (one vowel, one syllable), the rhyme rule handles open and closed endings, and `brief.py --lang ru` adds `Russian-language vocals, clear diction` to the style prompt and switches the lyric brief to Russian budgets. `references/russian-vocals.md` is in Russian.

</details>

<details>
<summary><b>Where do the character limits come from?</b></summary>

They are defaults in `suno_lint.py` (`--max-style 1000`, `--max-lyrics 5000`), chosen to be on the safe side. The Suno editor shows the current limit next to each field; pass the flag if yours differs.

</details>

<details>
<summary><b>Does this generate music?</b></summary>

No. It writes the inputs (style prompt, structure, lyrics) and checks them. You paste them into Suno. UniqAI does not generate music either.

</details>

## Contributing

Issues and pull requests are welcome. Keep changes small and include a before/after example in the PR description. See [CONTRIBUTING.md](CONTRIBUTING.md) for the local checks (`python3 tests/run.py`, no dependencies).

## License

Code and skill: [MIT](LICENSE) © UniqAI. The prompt libraries in `references/` are CC BY 4.0 (attribution: UniqAI, https://github.com/uniqaiapp/suno-producer); the [LICENSE](LICENSE) file says which paths fall under which.

---

<div align="center">

<sub>Made by <a href="https://uniqai.app/?utm_source=github&utm_medium=readme&utm_campaign=suno-producer">UniqAI</a> — Kling 3.0, Veo 3, Flux, Nano Banana and GPT-5/Claude/Gemini/Grok in one app.</sub>

</div>
