# Section tags

Tags go in the **Lyrics** field, one per line, in square brackets, Capitalised. Suno reads them as structure hints; words it does not recognise as structure it may sing. The lint (`scripts/suno_lint.py`) warns on anything outside this list (rule `L001`), so if you add a tag that works for you, add it to `KNOWN_TAGS` in the script and to this file in the same pull request.

## Structure tags

| Tag | What it does | Lines under it |
|---|---|---|
| `[Intro]` | Opens the song; usually instrumental | none, or one sung line |
| `[Verse]`, `[Verse 1]`, `[Verse 2]` | Story sections; numbering helps the model keep them distinct | 4 (sometimes 8) |
| `[Pre-Chorus]` | Lift into the chorus; tension | 2 |
| `[Chorus]` | The repeated section; title phrase lives here | 4 |
| `[Post-Chorus]` | Chant or repeated title after the chorus | 1–2 |
| `[Hook]` | Short repeated line(s); hip hop, lo-fi, pop | 2–4 |
| `[Refrain]` | A repeated line at the end of each verse (folk) | 1 |
| `[Bridge]` | New angle, often a key or energy change | 2–4 |
| `[Build]`, `[Build-Up]` | Rising energy before a drop | 0–2 |
| `[Drop]` | EDM payoff; mostly instrumental or a chopped phrase | 0–1 |
| `[Breakdown]` | Stripped section after a drop | 2 |
| `[Interlude]` | Short instrumental or spoken gap | 0–1 |
| `[Instrumental]` | Explicitly no vocals | none |
| `[Solo]`, `[Guitar Solo]`, `[Piano Solo]`, `[Synth Solo]`, `[Sax Solo]` | Lead instrument section | none |
| `[Break]` | Short rhythmic pause | none |
| `[Outro]` | Closes the song | 1–2, or a repeated title line |
| `[End]`, `[Fade Out]` | Hard stop / fade; place last | none |

## Delivery tags

Put these on their own line before the lines they affect. They change how the next lines are sung, not the structure.

| Tag | Effect to expect |
|---|---|
| `[Spoken]`, `[Spoken Word]` | Talked, not sung |
| `[Rap Verse]`, `[Rap]` | Rapped delivery |
| `[Whisper]` | Quiet, close vocal |
| `[Shout]`, `[Chant]`, `[Crowd]`, `[Gang Vocals]` | Group or raised delivery |
| `[Ad-Libs]`, `[Vocal Run]` | Decorative vocal, works best with `(parenthesised)` words |
| `[Acapella]` | Vocal only |
| `[Half-Time]`, `[Double-Time]` | Tempo feel change for the section |
| `[Key Change]` | Modulation, usually before the last chorus |
| `[Big Finish]`, `[Silence]` | Ending gestures |

## Parentheses

`(like this)` on its own line = backing vocal, echo or ad-lib. Inside a line, `(oh-oh)` is sung as a response. `lyric_meter.py` excludes whole-line parentheses from the length check, since they are short by design.

## Placement rules the lint enforces

- Nothing before the first tag (`L002`); `[Intro]` first, `[Outro]` last (`L005`).
- A tag on its own line, never `[Chorus] la la la` (`L010`).
- One tag per section start; `[Chorus]` twice in a row is a mistake (`L004`); an empty `[Verse]` is a mistake (`L016`), an empty `[Intro]` or `[Guitar Solo]` is normal.
- Twelve lines per section is the default ceiling (`L011`); long sections get compressed or cut.
- Balanced brackets on every line (`L006`).
- Tags belong in the lyrics field, not the style field (`L012`).
