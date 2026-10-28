# Examples

Every file in `outputs/` is produced by the command next to it, from the inputs in this folder. `python3 tests/run.py` re-runs each command and fails if the output differs by a byte; `python3 examples/regen.py` rewrites them after an intentional change. The list of commands is `manifest.json`.

| Output | Command | What it shows |
|---|---|---|
| `outputs/midnight-bus.meter.txt` | `python3 scripts/lyric_meter.py examples/lyrics/midnight-bus.txt` | Syllables and rhyme scheme per section of an English synthwave / indie-pop song; no warnings |
| `outputs/midnight-bus.meter.json` | `python3 scripts/lyric_meter.py --json examples/lyrics/midnight-bus.txt` | Same report as JSON (per-line syllables, rhyme letter, ending key) |
| `outputs/severny-veter.meter.txt` | `python3 scripts/lyric_meter.py examples/lyrics/severny-veter.ru.txt` | Russian rock ballad: 10-syllable verses, 8-syllable choruses, full and slant rhymes |
| `outputs/midnight-bus.lint.txt` | `python3 scripts/suno_lint.py examples/lyrics/midnight-bus.txt --style examples/style/midnight-bus.txt` | A clean pass |
| `outputs/severny-veter.lint.txt` | `python3 scripts/suno_lint.py examples/lyrics/severny-veter.ru.txt --style examples/style/severny-veter.ru.txt` | A clean pass on Russian lyrics |
| `outputs/bad-tags.lint.txt` | `python3 scripts/suno_lint.py examples/lyrics/bad-tags.txt --style examples/style/bad-style.txt` | Exit 1; most rules firing on a deliberately broken file and style prompt |
| `outputs/brief-synthwave-indie-pop.txt` | `python3 scripts/brief.py --genre synthwave --fuse "indie pop" --mood melancholic --seed 7` | Style prompt A with one-axis variants B and C, structure, lyric brief |
| `outputs/brief-russian-rock.ru.txt` | `python3 scripts/brief.py --genre "russian rock" --mood dark --lang ru --seed 3` | Russian-language brief: language descriptors in the style prompt, Russian lyric notes |
| `outputs/brief-house.json` | `python3 scripts/brief.py --genre house --mood euphoric --variants 4 --seed 11 --json` | Four variants (base, vocal, production, tempo) as JSON |
| `outputs/brief-list.txt` | `python3 scripts/brief.py --list` | Available genres, moods, vocal types and structures |

## Inputs

- `lyrics/midnight-bus.txt` + `style/midnight-bus.txt`: a complete English song, original lyrics written for this repo.
- `lyrics/severny-veter.ru.txt` + `style/severny-veter.ru.txt`: a complete Russian song, original lyrics written for this repo.
- `lyrics/bad-tags.txt` + `style/bad-style.txt`: a file that breaks most lint rules on purpose.

All lyrics here are original and released under the repo's MIT license. Do not add copyrighted lyrics as examples.
