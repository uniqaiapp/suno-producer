# Troubleshooting: symptom → one change

Change one thing, regenerate twice, compare. Run `scripts/suno_lint.py` before every retry.

| Symptom | Likely cause | Change |
|---|---|---|
| The vocal sings the word "Chorus" or "Verse" | Tag not recognised (misspelt, lower-case, inline with lyrics) | Fix the tag to a known one from `section-tags.md`, on its own line; lint `L001`, `L010`, `L014` |
| First lines are sung as a verse, no intro | Lyrics before the first tag | Move them under `[Verse 1]`; lint `L002` |
| Chorus sounds different each time | Chorus text differs between occurrences | Paste the identical block every time |
| A section is rushed or words are dropped | Lines of uneven length | `lyric_meter.py`; cut the long lines to the section median |
| Second verse is a melody-less mumble | Verse longer than twelve lines, or two verses merged | Split into `[Verse 2]` and `[Verse 3]`; lint `L011` |
| No bridge in the output | Bridge is one line, or the song is already long | Give it two to four lines; or drop a chorus before it |
| Wrong genre | Genre word late in the style prompt, or two conflicting genres | Move genre first; keep one fusion genre at most |
| Wrong language, or accented | Language not stated, or stated in the lyrics | Add `Russian-language vocals, clear diction` (or the language) at the end of the style prompt |
| Vocal buried in the mix | No vocal descriptor | Add one (`warm female vocal`, `low male vocal`); for RU add `vocal up front` |
| Song ends abruptly | No `[Outro]` or `[End]` | Add `[Outro]` with one repeated title line, then `[End]` |
| Song does not stop, fades into noise | `[Fade Out]` missing or too much lyric after the outro | Put `[Fade Out]` last, nothing after it |
| Rejected: artist name | Name or "in the style of" in either field | Translate to sound words (`style-prompts.md`); lint `L007` |
| The drop is sung over | Lyrics under `[Drop]` | Leave `[Drop]` empty or one `(parenthesised)` phrase |
| Tempo feels wrong | No tempo in the style prompt | Add `NN BPM`; lint `L015` |
| Instrumental has random vocals | `instrumental` descriptor missing, or stray lyric lines | Add `instrumental` to style, remove every lyric line, keep tags; run lint with `--instrumental` |
