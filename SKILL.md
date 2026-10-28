---
name: suno-producer
description: Writes Suno-ready song briefs from a plain description: a comma-separated style prompt (genre, fusion, BPM, key, mood, instruments, production, vocal), a section structure with tags ([Intro], [Verse], [Pre-Chorus], [Chorus], [Drop], [Bridge], [Outro]), lyrics that fit the structure, and A/B variants that change one axis at a time, then checks the result with a syllable/rhyme meter and a tag lint (English and Russian). Use when the user asks for a Suno prompt, Suno style tags or meta-tags, a song structure, lyrics for Suno, an AI song, "напиши песню для Suno", "промпт для Suno", "теги Suno", or pastes lyrics and asks why Suno rushed or ignored a section. Not for mixing or mastering advice, for other music models' syntax, for reproducing existing copyrighted lyrics, or for imitating a named artist.
license: MIT
metadata:
  version: 0.1.0
  author: UniqAI
  homepage: https://github.com/uniqaiapp/suno-producer
---

# Suno producer

Turn "a sad synthwave song about a night bus, female vocal" into something Suno can actually follow: a style prompt that describes sound rather than names, a tagged structure, lyrics whose lines are the same length inside each section, and two or three variants that differ in exactly one thing. The most common trigger is "write me a Suno prompt for ...". It is written for the two fields the Suno editor exposes, Style and Lyrics (v4.5 at the time of writing, 2026-10); the field budgets are defaults you can override. The scripts are plain Python 3 with no packages.

## When to use

- The user wants a Suno prompt, style tags, meta-tags, or a lyrics layout with `[Section]` tags.
- The user has an idea ("wedding song, acoustic, Russian") and wants a complete brief: style, structure, lyrics.
- The user pastes lyrics or a style prompt and asks why Suno sang the tag names, rushed a section, ignored the chorus, or produced the wrong genre.
- The user wants to A/B test a song: which vocal, tempo or production change made the difference.
- Russian-language lyrics (see `references/russian-vocals.md`): syllable budgets and diction notes differ from English.

## When NOT to use

- Mixing, mastering, stems, or anything after the generation step.
- Other models (Udio, MusicGen, Stable Audio): the tag vocabulary and field limits differ; only the lyric-craft part transfers.
- Requests to reproduce or lightly rewrite existing copyrighted lyrics. Decline and offer an original lyric on the same theme.
- "In the style of <living artist>". Suno rejects artist names and the request is an imitation; describe the sound instead (`references/style-prompts.md` has the translation table: artist → era, instruments, production, vocal).
- Instrumental-only requests that need no lyrics: use only step 2 and `scripts/brief.py`.

## How it works

1. **Clarify the brief in one question or none.** You need: genre (one, or two to fuse), mood, language of the vocal, vocal type (female / male / duet / none), rough length (short: five sections; standard: ten), and the song's one sentence ("what happens"). If the user gave most of this, do not ask; pick sensible defaults and say which you picked.

2. **Generate the skeleton.** Run

   ```bash
   python3 scripts/brief.py --genre "<genre>" [--fuse "<genre2>"] --mood <mood> --vocal <type> --lang en|ru [--bpm N] [--key "A minor"] --variants 3 --seed <any int>
   ```

   It prints: style prompt A plus variants B/C (each changes one axis: vocal, production, tempo), the section structure for that genre, and a lyric brief with lines-per-section and syllable targets. `--list` shows the available genres, moods, vocal types and structures; unknown genres fail loudly rather than guessing. The genre table is `references/genres.json`; extend it when the user's genre is missing instead of inventing descriptors in prose.

3. **Write the style prompt by hand if the generated one is off.** Rules (full list in `references/style-prompts.md`):
   - One line, comma-separated descriptors, most important first: genre, fusion genre, tempo (`104 BPM` or a feel word), key, two mood words, two or three instruments, one or two production words, the vocal, then language if not English.
   - Sound words, never names: no artists, bands, song titles or labels.
   - No `[tags]` in the style field, no sentences, no "a song about…" (that goes in the lyrics).
   - Keep it well under the field limit; the lint defaults to 1000 characters, override with `--max-style` if the editor shows another number.

4. **Write the lyrics into the structure.** Rules (details and examples in `references/lyric-craft.md`):
   - One tag per line, Capitalised, on its own line: `[Verse 1]`, `[Pre-Chorus]`, `[Chorus]`. Tags from `references/section-tags.md`; anything else may be sung aloud.
   - Lines inside a section stay within about two syllables of each other; verses 7–9 syllables in English (8–11 in Russian), choruses shorter and simpler than verses.
   - The chorus carries the title phrase on its first and last line and repeats verbatim each time. The bridge never reuses the title line.
   - Concrete nouns over abstractions; one scene per verse; the pre-chorus ends unresolved.
   - Backing vocals and ad-libs go in `(parentheses)` on their own line.
   - Nothing before the first tag; `[Intro]` first, `[Outro]` last; `[Instrumental]`, `[Guitar Solo]`, `[Drop]` may be empty.

5. **Check, then fix.** Run both scripts and act on every line they print:

   ```bash
   python3 scripts/lyric_meter.py lyrics.txt            # syllables per line, rhyme scheme per section, length drift
   python3 scripts/suno_lint.py lyrics.txt --style style.txt   # tag, structure, budget and imitation checks
   ```

   `lyric_meter` prints `[Verse 1]  4 lines · syllables 7-8 · scheme ABAB` per section and `!` warnings for lines that drift from the section median. Fix drift by cutting words, not by adding filler. Lowercase letters in a scheme are slant rhymes; decide whether they are intentional. `suno_lint` exits 1 on errors (unbalanced tags, artist phrases, over-budget fields) and lists warnings with stable rule ids (`L001`–`L016`); the README has the table.

6. **Deliver in this order, nothing else between the blocks:**

   ```
   Style (paste into Style):
   <one line>

   Lyrics (paste into Lyrics):
   [Intro]
   ...

   Variants to try (change one thing each):
   B (vocal): <line>
   C (production): <line>
   ```

   Then two or three sentences: what the user should listen for in A vs B vs C, and the one thing to change next if the chorus does not land (usually: shorter chorus lines, or a `[Pre-Chorus]` that ends unresolved).

7. **If the user comes back with a result** ("it sang the word Chorus", "the bridge is missing", "it rushed the second verse"), look up the symptom in `references/troubleshooting.md` and change one thing at a time; re-run the lint before handing back.

## Inputs / outputs

| Input | Output |
|---|---|
| A sentence describing the song (genre, mood, language, vocal) | Style prompt A + variants B/C, structure, lyric brief (`scripts/brief.py`) |
| Lyrics with `[Section]` tags | Syllables per line, rhyme scheme per section, drift warnings (`scripts/lyric_meter.py`) |
| Lyrics + style prompt | Errors/warnings with rule ids and line numbers, exit code (`scripts/suno_lint.py`) |
| A failed generation described in words | A single change from `references/troubleshooting.md` |

All scripts take `--json` for machine-readable output and `--help` for the flags.

## Examples

- `examples/lyrics/midnight-bus.txt` with `examples/style/midnight-bus.txt`: a complete English synthwave/indie-pop song that passes the lint clean; output in `examples/outputs/midnight-bus.*`.
- `examples/lyrics/severny-veter.ru.txt`: a Russian rock ballad with 10-syllable verses and 8-syllable choruses; `examples/outputs/severny-veter.meter.txt` shows the meter report.
- `examples/lyrics/bad-tags.txt`: a deliberately broken file that trips most lint rules; see `examples/outputs/bad-tags.lint.txt`.
- `python3 scripts/brief.py --genre synthwave --fuse "indie pop" --mood melancholic --seed 7` reproduces `examples/outputs/brief-synthwave-indie-pop.txt`.

`examples/README.md` lists the exact command for every committed output.

## Limits

- Syllable counts are heuristics: English is usually within one syllable of a dictionary count (words like "fire", "idea", "every" are the usual misses); Russian counts vowels, which is exact for standard spelling but counts "в" and "к" as zero (correct for singing).
- Rhyme detection compares word endings without stress data, so it finds full and slant rhymes but cannot tell a feminine from a masculine rhyme in Russian.
- Field budgets (`--max-style`, `--max-lyrics`) are defaults, not a spec; the Suno editor shows the live limit.
- The genre table is editorial: typical tempo ranges and instrument lists, not measurements. Treat it as a starting point and edit `references/genres.json`.
- The scripts do not call Suno and cannot predict whether a generation will be good; they remove the known causes of bad ones.

## References

- `references/section-tags.md`: every tag the lint knows, what it does, and where it goes.
- `references/style-prompts.md`: descriptor order, vocabulary by axis, artist-to-sound translation, length rules.
- `references/lyric-craft.md`: syllable budgets, rhyme schemes, hook placement, cliché list, worked example.
- `references/russian-vocals.md`: Russian-language specifics (slogi, ударение, ё, diction words for the style field).
- `references/ab-testing.md`: how to run one-axis variants and read the results.
- `references/troubleshooting.md`: symptom → single change.
- `references/genres.json`: the data behind `scripts/brief.py`.
