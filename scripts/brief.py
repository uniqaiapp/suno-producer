#!/usr/bin/env python3
"""brief.py: turn a plain description into a Suno-ready brief: style prompt, A/B variants,
section structure and a lyric brief with per-section syllable and rhyme targets.

Zero dependencies. Genre data lives in references/genres.json (edit it, add genres).

    python3 scripts/brief.py --genre synthwave --fuse "indie pop" --mood melancholic
    python3 scripts/brief.py --genre "russian rock" --mood dark --lang ru --vocal male
    python3 scripts/brief.py --genre house --bpm 124 --key "F minor" --variants 4 --seed 11
    python3 scripts/brief.py --list

Variants change exactly one axis each (vocal, production, tempo), so an A/B test tells
you which change mattered. Output is deterministic for a given --seed.
"""
import argparse
import json
import os
import random
import sys

__version__ = "0.1.0"
HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(os.path.dirname(HERE), "references", "genres.json")

SECTION_BRIEF_EN = {
    "intro":       "instrumental or one sung line; sets tempo and the main instrument. Leave empty or one line.",
    "verse":       "4 lines, 7-9 syllables, scheme ABAB or AABB; one scene, concrete nouns, no abstractions.",
    "pre-chorus":  "2 lines, rising; end on an unresolved thought that the chorus answers.",
    "chorus":      "4 lines, 5-8 syllables; title phrase on line 1 and line 4; simplest words in the song.",
    "post-chorus": "1-2 lines, a chant or the title repeated; vowels, not consonants.",
    "hook":        "2-4 lines, 4-7 syllables, repeated verbatim every time; one idea only.",
    "build":       "2 lines or none; short words, rising energy; can be the hook spoken.",
    "drop":        "instrumental, or one repeated phrase in (parentheses) for the model to chop.",
    "breakdown":   "2 lines, half the density of a verse; strip to vocal and one instrument.",
    "bridge":      "2-4 lines, new angle or a reply to the chorus; never reuse the title line.",
    "guitar solo": "instrumental; no lyrics, keep the tag alone on its line.",
    "interlude":   "instrumental or a single spoken line.",
    "outro":       "repeat the title line once or twice, then (fade out) or a final short line.",
}
SECTION_BRIEF_RU = {
    "intro":       "инструментал или одна строка; задаёт темп и главный инструмент.",
    "verse":       "4 строки, 8-11 слогов, схема ABAB или AABB; одна сцена, конкретные существительные.",
    "pre-chorus":  "2 строки на подъёме; закончить незавершённой мыслью, на которую отвечает припев.",
    "chorus":      "4 строки, 6-9 слогов; строка-название в 1-й и 4-й строке; самые простые слова в песне.",
    "post-chorus": "1-2 строки, повтор названия; гласные, а не согласные.",
    "hook":        "2-4 строки, 5-8 слогов, повторяется слово в слово; одна мысль.",
    "build":       "2 строки или пусто; короткие слова, нарастание.",
    "drop":        "инструментал или одна фраза в (скобках).",
    "breakdown":   "2 строки, вдвое реже, чем куплет; только голос и один инструмент.",
    "bridge":      "2-4 строки, новый угол или ответ припеву; строку-название не повторять.",
    "guitar solo": "инструментал; тег один на строке.",
    "interlude":   "инструментал или одна строка речитативом.",
    "outro":       "повтор строки-названия один-два раза, затем (fade out).",
}


def load_data(path=DATA):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def base(tag):
    t = tag.lower()
    return t.rsplit(" ", 1)[0] if t[-1:].isdigit() else t


def build(data, genre, fuse=None, mood=None, vocal=None, bpm=None, key=None, lang="en",
          structure=None, variants=3, seed=1):
    g = data["genres"].get(genre)
    if g is None:
        raise SystemExit("unknown genre %r; run --list" % genre)
    f = data["genres"].get(fuse) if fuse else None
    if fuse and f is None:
        raise SystemExit("unknown genre %r; run --list" % fuse)
    rng = random.Random(seed)

    lo, hi = g["bpm"]
    if f:
        lo2, hi2 = f["bpm"]
        olo, ohi = max(lo, lo2), min(hi, hi2)
        if olo <= ohi:
            lo, hi = olo, ohi
    tempo = bpm if bpm else int(round((lo + hi) / 2 / 2.0) * 2)
    key = key or rng.choice(g["keys"])
    mood_key = mood or rng.choice(sorted(data["moods"]))
    moods = data["moods"].get(mood_key)
    if moods is None:
        raise SystemExit("unknown mood %r; run --list" % mood_key)
    mood_words = moods[:2]
    vocal_key = vocal or g.get("default_vocal", "female")
    vocal_list = data["vocals"].get(vocal_key)
    if vocal_list is None:
        raise SystemExit("unknown vocal %r; run --list" % vocal_key)

    instruments = rng.sample(g["instruments"], min(2, len(g["instruments"])))
    production = [rng.choice(g["production"])]
    if f:
        instruments += rng.sample(f["instruments"], 1)
        production.append(rng.choice(f["production"]))
    lang_words = ["Russian-language vocals", "clear diction"] if lang == "ru" and vocal_key != "none" else []

    def prompt(tempo_, feel, vocal_word, prod):
        parts = [genre] + ([fuse] if fuse else []) + ["%d BPM" % tempo_, key] + mood_words + instruments + prod + [vocal_word] + lang_words
        return ", ".join(p for p in parts if p)

    feel = g["feel"]
    vocal_a = vocal_list[0]
    out = [{"id": "A", "axis": "base", "prompt": prompt(tempo, feel, vocal_a, production)}]
    axes = []
    if len(vocal_list) > 1:
        axes.append(("vocal", lambda: prompt(tempo, feel, vocal_list[1], production)))
    alt_prod = [p for p in g["production"] if p not in production]
    if alt_prod:
        axes.append(("production", lambda: prompt(tempo, feel, vocal_a, [rng.choice(alt_prod)] + production[1:])))
    alt_tempo = max(lo, min(hi, int(round(tempo * 1.08 / 2.0) * 2))) if tempo < hi else max(lo, int(round(tempo * 0.92 / 2.0) * 2))
    if alt_tempo != tempo:
        axes.append(("tempo", lambda: prompt(alt_tempo, feel, vocal_a, production)))
    for i, (axis, fn) in enumerate(axes[:max(0, variants - 1)]):
        out.append({"id": chr(ord("B") + i), "axis": axis, "prompt": fn()})

    struct_name = structure or g.get("structure", "pop")
    sections = data["structures"].get(struct_name)
    if sections is None:
        raise SystemExit("unknown structure %r; run --list" % struct_name)
    briefs = SECTION_BRIEF_RU if lang == "ru" else SECTION_BRIEF_EN
    lyric_brief = []
    seen = set()
    for s in sections:
        b = base(s)
        if b in seen:
            continue
        seen.add(b)
        lyric_brief.append({"section": s, "note": briefs.get(b, "")})
    return {
        "genre": genre, "fuse": fuse, "mood": mood_key, "vocal": vocal_key, "bpm": tempo, "bpm_range": [lo, hi],
        "key": key, "lang": lang, "feel": feel, "structure": struct_name, "sections": sections,
        "style_prompts": out, "lyric_brief": lyric_brief, "seed": seed,
    }


def format_text(b):
    title = b["genre"] + (" x " + b["fuse"] if b["fuse"] else "")
    lines = ["suno-producer brief  %s" % title,
             "tempo %d BPM (range %d-%d) · key %s · mood %s · vocal %s · lang %s · seed %d"
             % (b["bpm"], b["bpm_range"][0], b["bpm_range"][1], b["key"], b["mood"], b["vocal"], b["lang"], b["seed"]),
             "", "Style prompt (paste into the Style field)"]
    for v in b["style_prompts"]:
        lines.append("  %s  [%s] %s" % (v["id"], v["axis"], v["prompt"]))
    lines += ["", "Structure (%s)" % b["structure"], "  " + " ".join("[%s]" % s for s in b["sections"]), "", "Lyric brief"]
    for item in b["lyric_brief"]:
        lines.append("  [%s] %s" % (item["section"], item["note"]))
    lines += ["", "Next", "  write the lyrics with these tags, then:",
              "  python3 scripts/lyric_meter.py lyrics.txt",
              "  python3 scripts/suno_lint.py lyrics.txt --style-text \"%s\"" % b["style_prompts"][0]["prompt"]]
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Suno brief generator: style prompt + A/B variants + structure + lyric targets.")
    ap.add_argument("--genre", help="primary genre (see --list)")
    ap.add_argument("--fuse", metavar="GENRE", help="second genre to fuse with")
    ap.add_argument("--mood", help="mood key (see --list); random by seed if omitted")
    ap.add_argument("--vocal", help="female | male | duet | choir | none (default: genre's)")
    ap.add_argument("--bpm", type=int, help="override tempo")
    ap.add_argument("--key", help="override key, e.g. 'A minor'")
    ap.add_argument("--lang", choices=["en", "ru"], default="en", help="lyric language (default en)")
    ap.add_argument("--structure", help="structure name (see --list); default: genre's")
    ap.add_argument("--variants", type=int, default=3, help="number of style prompts incl. A (1-4, default 3)")
    ap.add_argument("--seed", type=int, default=1, help="random seed for deterministic picks (default 1)")
    ap.add_argument("--data", default=DATA, help="path to genres.json")
    ap.add_argument("--list", action="store_true", help="list genres, moods, vocals, structures")
    ap.add_argument("--json", action="store_true", help="print JSON")
    ap.add_argument("--version", action="version", version=__version__)
    a = ap.parse_args(argv)
    data = load_data(a.data)
    if a.list:
        print("genres:     " + ", ".join(sorted(data["genres"])))
        print("moods:      " + ", ".join(sorted(data["moods"])))
        print("vocals:     " + ", ".join(sorted(data["vocals"])))
        print("structures: " + ", ".join(sorted(data["structures"])))
        return 0
    if not a.genre:
        ap.error("--genre is required (or --list)")
    b = build(data, a.genre.lower(), a.fuse.lower() if a.fuse else None, a.mood, a.vocal, a.bpm, a.key,
              a.lang, a.structure, max(1, min(4, a.variants)), a.seed)
    print(json.dumps(b, ensure_ascii=False, indent=2) if a.json else format_text(b))
    return 0


if __name__ == "__main__":
    sys.exit(main())
