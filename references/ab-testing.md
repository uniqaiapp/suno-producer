# A/B variants

Generations are noisy: the same prompt gives different songs. A variant that changes three things at once tells you nothing, because you cannot say which change did it. So every variant here changes exactly one axis, and `tests/test_brief.py` enforces that `brief.py` keeps it that way (one descriptor differs between A and each variant).

## The three axes

| Variant | Axis | What changes | Listen for |
|---|---|---|---|
| B | vocal | one vocal descriptor (`warm female vocal` → `breathy female vocal`) | Does the chorus feel closer or further away? Does diction improve? |
| C | production | one production word (`80s production` → `wide stereo pads`) | Width, era, how much space the vocal has |
| D | tempo | BPM ±8 %, within the genre range | Does the verse breathe? Do chorus lines land on the beat? |

Run A and each variant twice (two generations each). If the difference is bigger *between* the two A runs than between A and B, the axis does not matter for this song; move on.

## Lyrics variants

Keep the style prompt fixed and change one thing in the lyrics:

- Chorus line length (cut one syllable per line).
- `[Pre-Chorus]` present vs absent.
- `[Key Change]` before the last chorus vs none.
- Title phrase on lines 1 and 4 vs line 1 only.

Re-run `lyric_meter.py` after each change; the variant must still be even inside each section or you are testing two things.

## Recording what you learned

Keep a two-column note per song: *change* → *what happened*. After three songs in a genre you will have a house style, which is worth more than any prompt list. Add generalisable findings to `references/genres.json` (a better default instrument, a narrower tempo range) by pull request, with the song file you tested on.
