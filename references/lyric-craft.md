# Lyric craft for generated vocals

Generated vocals have one weakness human singers do not: they cannot stretch or rush a line to make it fit. If line 3 of a verse has twelve syllables and the others have eight, the model either rushes the words or drops some. So the craft here is mostly about *evenness*, and the scripts measure it.

## Syllable budgets

| Section | English | Russian | Why |
|---|---|---|---|
| Verse | 7–9 per line | 8–11 | Enough room for an image; still sits on a 4-bar phrase |
| Pre-Chorus | 6–9 | 7–10 | Shorter than the verse so the lift feels like compression |
| Chorus | 5–8 | 6–9 | Short lines are what people sing back |
| Hook | 4–7 | 5–8 | One breath |
| Bridge | 6–10 | 7–11 | Looser; it is the one place variety reads as intent |

Inside a section, keep every line within two syllables of the section median; `lyric_meter.py` warns past that (`--max-deviation`). Across sections, the chorus should be visibly shorter than the verse in the report.

## Rhyme schemes

- **Verse:** `ABAB` or `AABB`. `ABCB` (only lines 2 and 4 rhyme) is the safest when the content fights the rhyme.
- **Chorus:** `AABB` or `AAAA`: denser rhyme than the verse, because repetition is the point.
- **Bridge:** `AA` couplet, or none.
- Slant rhymes (shown lowercase in the meter report, e.g. `ABaB`) are fine in verses and weak in choruses.
- Never rhyme a word with itself except in a deliberate refrain.

## The chorus

1. Title phrase on line 1 and line 4 (or line 1 only in a 2-line hook).
2. Same words every time it appears. Write it once, paste it. The model sings a varied chorus as a new section.
3. The simplest vocabulary in the song. Save the good nouns for the verses.
4. Open vowels on the long notes: words ending in `-ay`, `-o`, `-ah`, `-ее`, `-а` sing; words ending in clusters (`-sts`, `-ств`) do not.

## The verse

- One scene per verse: a place, a time, one or two concrete objects. "Streetlights hum a tired song / Rain keeps tapping on the glass" sets a bus at night in two lines; "I feel so lost and so alone" sets nothing.
- Verse 2 moves the scene (time passes, the camera turns), it does not restate verse 1.
- End the pre-chorus on an unfinished thought so the chorus answers it.

## The bridge

New angle: the other person's view, the morning after, the thing left unsaid. Never the title line (`brief.py` repeats this in its lyric brief). A `[Key Change]` tag before the last chorus is the classic way to make the bridge pay off.

## Words to cut

Generated-lyric clichés that the model also over-produces on its own. If one appears, replace it with an object you can photograph.

`neon lights` · `city of dreams` · `through the storm` · `rise above` · `we are unstoppable` · `fire in my soul` · `broken wings` · `shadows of the past` · `echoes in the night` · `heartbeat of the city` · `in the end` · `forever and always`

Russian equivalents are in `references/russian-vocals.md`.

## Worked example

`examples/lyrics/midnight-bus.txt` with its meter report `examples/outputs/midnight-bus.meter.txt`:

```
[Verse 1]      4 lines · syllables 6-8 · scheme ABAB
[Pre-Chorus]   2 lines · syllables 8-9 · scheme AA
[Chorus]       4 lines · syllables 6-9 · scheme AABB
```

The chorus line 3 ("Every window's a telephone", 9) is the longest in the song and one syllable over the chorus budget; it stays because "telephone" is the image the title pays off, and the model sings a single long line fine when its neighbours are even. That is the kind of judgement the report is for: it tells you where the risk is, you decide.

## Process

1. `python3 scripts/brief.py …` for the structure and budgets.
2. Write the chorus first. If it is not singable alone, nothing else will save it.
3. Write verse 1, then verse 2 as a second scene, then the pre-chorus, then the bridge.
4. `python3 scripts/lyric_meter.py lyrics.txt`, fix drift by cutting.
5. `python3 scripts/suno_lint.py lyrics.txt --style style.txt`, fix every `x`, decide on every `!`.
