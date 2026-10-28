# Style prompts

The **Style** field describes the *sound*. The lyrics field carries the words and the structure. Mixing the two is the single most common cause of a generation that ignores half of what you asked for.

## Order of descriptors

One line, commas, most important first. The model weights early descriptors more.

```
<genre>, <fusion genre>, <tempo>, <key>, <mood>, <mood>, <instrument>, <instrument>, <instrument>, <production>, <production>, <vocal>, <language>
```

Example (from `examples/style/midnight-bus.txt`):

```
synthwave, indie pop, 104 BPM, A minor, melancholic, wistful, analog synth arpeggios, gated reverb drums, jangly electric guitar, 80s production, room reverb, warm female vocal
```

Twelve descriptors is a comfortable size. Past about twenty, later descriptors stop mattering and start contradicting earlier ones.

## Vocabulary by axis

**Tempo.** A number with `BPM` (`92 BPM`) or a feel word: `slow`, `mid-tempo`, `uptempo`, `fast`, `driving`, `laid-back`, `half-time feel`. Use one, not both, unless the number and the feel disagree on purpose (`140 BPM, half-time feel` for trap).

**Key.** `A minor`, `F# minor`, `C major`. Minor keys pull toward melancholic and dark moods; major toward warm and playful. Optional, but it stabilises the melody between variants.

**Mood.** Two words, adjacent not identical: `melancholic, wistful`; `dark, cinematic`; `warm, nostalgic`; `euphoric, anthemic`. Three or more mood words blur.

**Instruments.** Name the three that define the genre, with one adjective each: `analog synth arpeggios`, `brushed drums`, `palm-muted power chords`, `Rhodes piano`, `808 bass`, `pedal steel`, `accordion`.

**Production.** Era and space: `80s production`, `90s East Coast production`, `lo-fi warmth`, `tape saturation`, `room reverb`, `club mix`, `live-in-a-room`, `sidechain compression`, `wide stereo pads`.

**Vocal.** Gender or type plus one adjective: `warm female vocal`, `gritty male vocal`, `breathy female vocal`, `low male vocal`, `male and female duet`, `layered choir`, `gang vocals`. For no vocals: `instrumental` and remove every lyric line.

**Language.** Only when not English: `Russian-language vocals, clear diction`; `Spanish-language vocals`. See `references/russian-vocals.md`.

## Artist names: translate, do not name

Suno rejects prompts that name artists, and the output would be an imitation anyway. Translate the reference into the axes above. The lint flags "in the style of", "sounds like", "в стиле", "как у" (`L007`).

| Instead of | Describe |
|---|---|
| a named 80s synth act | `synthwave, 80s production, gated reverb drums, analog synth arpeggios, breathy female vocal` |
| a named 90s boom-bap producer | `boom bap, 90 BPM, chopped soul sample, punchy kick and snare, vinyl texture, gritty male vocal` |
| a named stadium rock band | `arena rock, anthemic, 120 BPM, big drums, layered guitars, gang vocals in the chorus` |
| a named Russian rock band | `russian rock, 90s Russian rock production, acoustic guitar intro, distorted guitars, raw mix, low male vocal, Russian-language vocals` |

Ask the user what they hear in the reference (era, instruments, vocal), then write those words.

## What not to put in the style field

- `[Tags]` of any kind (`L012`).
- Sentences: "a song about a girl who…". That is lyric content; move it to the lyrics or drop it.
- The song title or lyrics lines.
- More than one language instruction.
- Contradictory tempo words (`slow, driving`).

## Length

The lint's default budget is 1000 characters for the style field and 5000 for lyrics (`--max-style`, `--max-lyrics`). These are defaults, not a specification: the Suno editor shows the live limit next to the field, and it has changed between versions. A good style prompt is nowhere near the limit; if you are counting characters, you are describing too much.
