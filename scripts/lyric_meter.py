#!/usr/bin/env python3
"""lyric_meter.py: syllable counter and rhyme-scheme checker for song lyrics (English and Russian).

Zero dependencies. Reads lyrics with Suno-style section tags ([Verse], [Chorus], ...),
counts syllables per line, derives the rhyme scheme per section and flags lines whose
length drifts from the section median.

    python3 scripts/lyric_meter.py lyrics.txt
    python3 scripts/lyric_meter.py --lang ru --json lyrics.ru.txt
    cat lyrics.txt | python3 scripts/lyric_meter.py -

Heuristics, not a dictionary: English counts are usually within one syllable of a
phonetic count; Russian counts are exact for standard spelling (one vowel = one syllable).
Rhyme detection compares word endings, so it finds full and slant rhymes but has no
notion of stress; see README "Limits".
"""
import argparse
import json
import re
import sys
from statistics import median

__version__ = "0.1.0"

TAG_RE = re.compile(r"^\s*\[([^\]]+)\]\s*$")
EN_VOWELS = "aeiouy"
RU_VOWELS = "аеёиоуыэюя"
CYRILLIC_RE = re.compile(r"[а-яё]", re.IGNORECASE)
LATIN_RE = re.compile(r"[a-z]", re.IGNORECASE)


# ----------------------------------------------------------------------------- syllables

def syllables_en(word):
    """Approximate syllable count for one English word."""
    w = re.sub(r"[^a-z]", "", word.lower().replace("'", ""))
    if not w:
        return 0
    if len(w) <= 3:
        return 1
    count = len(re.findall(r"[aeiouy]+", w))
    # silent final e: "time", "love" (but not "table", "free", "eye")
    if w.endswith("e") and not w.endswith(("le", "ee", "ye", "oe", "ue")) and count > 1:
        count -= 1
    # -ed is silent unless after t/d: "walked" 1, "wanted" 2
    elif w.endswith("ed") and not re.search(r"[td]ed$", w) and count > 1:
        count -= 1
    # -es is silent unless after a sibilant: "waves" 1, "boxes" 2
    elif w.endswith("es") and not re.search(r"(ss|sh|ch|x|z|[cg])es$", w) and count > 1:
        count -= 1
    # vowel pairs that are usually two syllables: "idea", "radio", "ruin", "create"
    count += len(re.findall(r"(?<=[^aeiouy])i[ao](?![nl])|ui(?!t)|eate", w))
    # -le after a consonant is its own syllable: "table", "little"
    if re.search(r"[^aeiouy]le$", w) and count == 1:
        count += 1
    return max(1, count)


def syllables_ru(word):
    """Syllable count for one Russian word: one vowel letter, one syllable."""
    w = word.lower()
    return sum(1 for ch in w if ch in RU_VOWELS)


def count_line(line, lang):
    words = tokenize(line)
    fn = syllables_ru if lang == "ru" else syllables_en
    return sum(fn(w) for w in words)


def tokenize(line):
    # drop stage directions in parentheses that are not sung words? No: Suno sings
    # parenthesised backing vocals, so keep them. Only drop the tag brackets.
    line = re.sub(r"\[[^\]]*\]", " ", line)
    return [w for w in re.findall(r"[A-Za-zА-Яа-яЁё']+", line) if re.search(r"[A-Za-zА-Яа-яЁё]", w)]


# ----------------------------------------------------------------------------- rhyme

def rhyme_key_en(word):
    w = re.sub(r"[^a-z]", "", word.lower().replace("'", ""))
    if not w:
        return ""
    core = w
    if len(core) > 3 and core.endswith("s") and not core.endswith("ss"):
        core = core[:-1]  # plural / 3rd person: miles -> mile
    if len(core) > 2 and core.endswith("e") and not core.endswith(("le", "ee", "ye", "oe", "ue")):
        core = core[:-1]  # silent e: time/rhyme -> tim/rhym
    m = re.search(r"[aeiouy]+[^aeiouy]*$", core)
    key = m.group(0) if m else core
    return key.replace("y", "i")


def rhyme_key_ru(word):
    w = word.lower().replace("ё", "о")
    if not w:
        return ""
    vowel_idx = [i for i, ch in enumerate(w) if ch in RU_VOWELS]
    if not vowel_idx:
        return w
    # Russian rhyme runs from the stressed vowel; without stress data take the last vowel and
    # its coda, and for open endings (word ends in a vowel) include the consonant before it,
    # so окно/давно -> "но"/"но" and дорога/нога -> "га"/"га".
    start = vowel_idx[-1]
    if start == len(w) - 1 and start > 0:
        start -= 1
    return w[start:]


def is_backing(line):
    """True when the whole line is a (parenthesised) backing vocal or ad-lib."""
    s = line.strip()
    return s.startswith("(") and s.endswith(")")


def last_word(line):
    words = tokenize(line)
    return words[-1] if words else ""


def rhyme_scheme(lines, lang):
    """Return (scheme string, keys). Uppercase = full rhyme, lowercase = slant rhyme."""
    keyfn = rhyme_key_ru if lang == "ru" else rhyme_key_en
    keys = [keyfn(last_word(ln)) for ln in lines]
    letters = []
    groups = []  # (letter, key)
    for key in keys:
        letter = None
        if key:
            for lt, k in groups:
                if k == key:
                    letter = lt
                    break
            if letter is None:
                for lt, k in groups:
                    if len(k) >= 2 and len(key) >= 2 and k[-2:] == key[-2:]:
                        letter = lt.lower()
                        break
        if letter is None:
            letter = chr(ord("A") + len(groups)) if len(groups) < 26 else "?"
            groups.append((letter, key))
        letters.append(letter)
    return "".join(letters), keys


# ----------------------------------------------------------------------------- parsing

def detect_lang(text):
    cyr = len(CYRILLIC_RE.findall(text))
    lat = len(LATIN_RE.findall(text))
    return "ru" if cyr > lat else "en"


def parse_sections(text):
    """Split lyrics into [(tag, [lines])]. Lines before the first tag go to tag ''."""
    sections = []
    tag, lines = "", []
    for raw in text.splitlines():
        line = raw.strip()
        m = TAG_RE.match(line)
        if m:
            if lines or tag:
                sections.append((tag, lines))
            tag, lines = m.group(1).strip(), []
            continue
        if not line:
            continue
        lines.append(line)
    if lines or tag:
        sections.append((tag, lines))
    return sections


# ----------------------------------------------------------------------------- report

def analyse(text, lang="auto", max_dev=2):
    if lang == "auto":
        lang = detect_lang(text)
    report = {"lang": lang, "sections": [], "warnings": []}
    for tag, lines in parse_sections(text):
        if not lines:
            report["sections"].append({"tag": tag, "lines": [], "scheme": "", "min": 0, "max": 0, "median": 0})
            continue
        counts = [count_line(ln, lang) for ln in lines]
        scheme, keys = rhyme_scheme(lines, lang)
        med = median(counts)
        sec = {
            "tag": tag, "scheme": scheme, "min": min(counts), "max": max(counts), "median": med,
            "lines": [{"n": i + 1, "syllables": c, "text": ln, "rhyme": scheme[i], "key": keys[i]}
                      for i, (ln, c) in enumerate(zip(lines, counts))],
        }
        report["sections"].append(sec)
        label = "[%s]" % tag if tag else "(untagged)"
        for i, c in enumerate(counts):
            if is_backing(lines[i]):
                sec["lines"][i]["backing"] = True
                continue  # (parenthesised) backing vocals are short by design
            if abs(c - med) > max_dev:
                sign = "+" if c > med else "-"
                report["warnings"].append("%s line %d has %d syllables, section median %g (%s%g)"
                                          % (label, i + 1, c, med, sign, abs(c - med)))
        if len(lines) >= 4 and len(set(scheme.upper())) == len(scheme):
            report["warnings"].append("%s has no rhymes in %d lines (scheme %s)" % (label, len(lines), scheme))
    return report


def format_text(report, name):
    out = ["lyric_meter  %s  (lang: %s)" % (name, report["lang"])]
    for sec in report["sections"]:
        label = "[%s]" % sec["tag"] if sec["tag"] else "(untagged)"
        if not sec["lines"]:
            out.append("%-14s empty" % label)
            continue
        span = "%d" % sec["min"] if sec["min"] == sec["max"] else "%d-%d" % (sec["min"], sec["max"])
        out.append("%-14s %d lines · syllables %s · scheme %s" % (label, len(sec["lines"]), span, sec["scheme"]))
        for ln in sec["lines"]:
            out.append("  %2d  %2d  %-44s %s" % (ln["n"], ln["syllables"], ln["text"][:44], ln["rhyme"]))
    for w in report["warnings"]:
        out.append("! " + w)
    if not report["warnings"]:
        out.append("+ no length or rhyme warnings")
    return "\n".join(out)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Syllable counter and rhyme-scheme checker for EN/RU lyrics with Suno section tags.")
    ap.add_argument("files", nargs="+", help="lyrics file(s); '-' reads stdin")
    ap.add_argument("--lang", choices=["auto", "en", "ru"], default="auto", help="language (default: auto-detect per file)")
    ap.add_argument("--max-deviation", type=int, default=2, metavar="N", help="warn when a line is more than N syllables from the section median (default 2)")
    ap.add_argument("--json", action="store_true", help="print JSON instead of text")
    ap.add_argument("--version", action="version", version=__version__)
    a = ap.parse_args(argv)
    reports = []
    for f in a.files:
        text = sys.stdin.read() if f == "-" else open(f, encoding="utf-8").read()
        rep = analyse(text, a.lang, a.max_deviation)
        rep["file"] = f
        reports.append(rep)
    if a.json:
        print(json.dumps(reports if len(reports) > 1 else reports[0], ensure_ascii=False, indent=2))
    else:
        print("\n\n".join(format_text(r, r["file"]) for r in reports))
    return 0


if __name__ == "__main__":
    sys.exit(main())
