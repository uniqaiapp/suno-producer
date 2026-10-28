#!/usr/bin/env python3
"""suno_lint.py: lint Suno-style lyrics and style prompts before you spend credits.

Zero dependencies. Checks section-tag placement and spelling, structure order, section
length, artist-imitation phrases, bracket balance, and the character budgets of the
style prompt and the lyrics field.

    python3 scripts/suno_lint.py lyrics.txt
    python3 scripts/suno_lint.py lyrics.txt --style style.txt
    python3 scripts/suno_lint.py lyrics.txt --style-text "indie pop, 110 BPM, warm female vocal"
    python3 scripts/suno_lint.py lyrics.txt --json --strict

Exit code 1 when any error is found (or any warning with --strict), else 0.
Rule ids are stable; see README "Lint rules" for the list.
"""
import argparse
import json
import re
import sys

__version__ = "0.1.0"

# Tags the Suno editor community uses consistently. Anything else is allowed, but warned,
# because unknown tags are often sung aloud instead of interpreted.
KNOWN_TAGS = {
    "intro", "verse", "pre-chorus", "chorus", "post-chorus", "hook", "drop", "build", "build-up",
    "breakdown", "bridge", "refrain", "interlude", "instrumental", "solo", "guitar solo", "break",
    "outro", "end", "fade out", "spoken", "spoken word", "rap verse", "rap", "ad-libs", "vocal run",
    "big finish", "silence", "half-time", "double-time", "key change", "acapella", "a cappella",
    "whisper", "shout", "chant", "crowd", "melodic", "catchy hook", "piano solo", "synth solo", "sax solo",
}
TAG_LINE_RE = re.compile(r"^\s*\[([^\]]*)\]\s*$")
INLINE_TAG_RE = re.compile(r"\[[^\]]*\]")
IMITATION_RE = re.compile(
    r"\b(in the style of|sounds? like|sounding like|like .{1,40} would sing|a la|à la|cover of|"
    r"в стиле|как у|под\s+\w+а\b|похож\w* на)\b", re.IGNORECASE)
DEFAULT_MAX_STYLE = 1000
DEFAULT_MAX_LYRICS = 5000
DEFAULT_MAX_SECTION_LINES = 12


def base_tag(tag):
    """'Verse 2' -> 'verse'; 'Chorus: big' -> 'chorus'; 'Pre-Chorus' -> 'pre-chorus'."""
    t = tag.strip().lower()
    t = re.split(r"[:(]", t)[0].strip()
    t = re.sub(r"\s*\d+\s*$", "", t)
    return t.strip()


def lint(lyrics, style=None, max_style=DEFAULT_MAX_STYLE, max_lyrics=DEFAULT_MAX_LYRICS,
         max_section_lines=DEFAULT_MAX_SECTION_LINES, instrumental=False):
    issues = []

    def add(level, rule, msg, line=None):
        issues.append({"level": level, "rule": rule, "message": msg, "line": line})

    lines = lyrics.splitlines()
    tags = []            # (line_no, raw_tag, base)
    section_lines = {}   # index in tags -> number of lyric lines
    seen_lyrics_before_tag = False
    prev_tag_line = None
    for i, raw in enumerate(lines, 1):
        line = raw.strip()
        if not line:
            continue
        if line.count("[") != line.count("]"):
            add("error", "L006", "unbalanced square brackets", i)
        if line.count("(") != line.count(")"):
            add("warn", "L006", "unbalanced parentheses", i)
        m = TAG_LINE_RE.match(line)
        if m:
            raw_tag = m.group(1).strip()
            b = base_tag(raw_tag)
            if not raw_tag:
                add("error", "L001", "empty tag []", i)
            elif b not in KNOWN_TAGS:
                add("warn", "L001", "unknown tag [%s]; Suno may sing it instead of following it" % raw_tag, i)
            if raw_tag and raw_tag[0].islower():
                add("warn", "L014", "tag [%s] is lower-case; write tags Capitalised for consistency" % raw_tag, i)
            if tags and prev_tag_line is not None and section_lines.get(len(tags) - 1, 0) == 0:
                if tags[-1][2] not in ("instrumental", "intro", "outro", "solo", "guitar solo", "piano solo",
                                       "synth solo", "sax solo", "break", "interlude", "drop", "build", "build-up",
                                       "breakdown", "silence", "fade out", "end", "key change", "half-time", "double-time"):
                    add("warn", "L016", "section [%s] has no lines" % tags[-1][1], tags[-1][0])
                if tags[-1][2] == b:
                    add("warn", "L004", "two [%s] tags in a row" % raw_tag, i)
            tags.append((i, raw_tag, b))
            section_lines[len(tags) - 1] = 0
            prev_tag_line = i
            continue
        if INLINE_TAG_RE.search(line):
            add("warn", "L010", "tag inside a lyric line; put each tag on its own line", i)
        if not tags:
            seen_lyrics_before_tag = True
        else:
            section_lines[len(tags) - 1] += 1
        if IMITATION_RE.search(line):
            add("error", "L007", "artist-imitation phrase in lyrics (\"%s\"); Suno rejects named artists" % IMITATION_RE.search(line).group(0), i)

    if seen_lyrics_before_tag:
        add("warn", "L002", "lyrics before the first section tag; Suno treats untagged text as a verse")
    bases = [b for _, _, b in tags]
    if not tags:
        if lyrics.strip() and not instrumental:
            add("warn", "L002", "no section tags at all; add [Verse] / [Chorus] so the structure is yours, not the model's")
    else:
        if "chorus" not in bases and "hook" not in bases and "drop" not in bases and not instrumental:
            add("warn", "L003", "no [Chorus], [Hook] or [Drop]; most songs need a repeated section")
        if "intro" in bases and bases[0] != "intro":
            add("warn", "L005", "[Intro] is not the first tag", tags[bases.index("intro")][0])
        if "outro" in bases and bases[-1] not in ("outro", "end", "fade out"):
            add("warn", "L005", "[Outro] is not the last tag", tags[bases.index("outro")][0])
        for idx, (ln, raw_tag, b) in enumerate(tags):
            n = section_lines.get(idx, 0)
            if n > max_section_lines:
                add("warn", "L011", "[%s] has %d lines (limit %d); long sections tend to get rushed or cut" % (raw_tag, n, max_section_lines), ln)
    total = len(lyrics)
    if total > max_lyrics:
        add("error", "L009", "lyrics are %d characters, over the %d budget" % (total, max_lyrics))

    if style is not None:
        s = style.strip()
        if not s:
            add("warn", "L008", "style prompt is empty")
        else:
            if len(s) > max_style:
                add("error", "L008", "style prompt is %d characters, over the %d budget" % (len(s), max_style))
            if INLINE_TAG_RE.search(s):
                add("warn", "L012", "style prompt contains [tags]; tags belong in the lyrics field")
            mm = IMITATION_RE.search(s)
            if mm:
                add("error", "L007", "artist-imitation phrase in style prompt (\"%s\"); describe the sound instead" % mm.group(0))
            if "\n" in s and len(s.splitlines()) > 3:
                add("warn", "L013", "style prompt has %d lines; one comma-separated line reads more reliably" % len(s.splitlines()))
            if not re.search(r"\b\d{2,3}\s?bpm\b", s, re.IGNORECASE) and not re.search(r"\b(slow|mid-tempo|uptempo|fast|driving|laid-back)\b", s, re.IGNORECASE):
                add("info", "L015", "style prompt has no tempo (e.g. '104 BPM' or 'mid-tempo')")
    return issues


def summarise(issues):
    counts = {"error": 0, "warn": 0, "info": 0}
    for it in issues:
        counts[it["level"]] += 1
    return counts


def format_text(issues, name):
    out = ["suno_lint  %s" % name]
    icon = {"error": "x", "warn": "!", "info": "i"}
    for it in sorted(issues, key=lambda x: (x["line"] or 0, x["rule"])):
        where = ("line %d: " % it["line"]) if it["line"] else ""
        out.append("%s %s  %s%s" % (icon[it["level"]], it["rule"], where, it["message"]))
    c = summarise(issues)
    if c["error"] == 0 and c["warn"] == 0:
        out.append("+ clean: 0 errors, 0 warnings" + (", %d info" % c["info"] if c["info"] else ""))
    else:
        out.append("= %d error(s), %d warning(s), %d info" % (c["error"], c["warn"], c["info"]))
    return "\n".join(out)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Lint Suno-style lyrics (section tags, structure, length) and style prompts.")
    ap.add_argument("lyrics", help="lyrics file with [Section] tags; '-' reads stdin")
    ap.add_argument("--style", metavar="FILE", help="style prompt file to lint alongside")
    ap.add_argument("--style-text", metavar="TEXT", help="style prompt given inline")
    ap.add_argument("--max-style", type=int, default=DEFAULT_MAX_STYLE, help="style prompt character budget (default %d; check the Suno editor for the current limit)" % DEFAULT_MAX_STYLE)
    ap.add_argument("--max-lyrics", type=int, default=DEFAULT_MAX_LYRICS, help="lyrics character budget (default %d)" % DEFAULT_MAX_LYRICS)
    ap.add_argument("--max-section-lines", type=int, default=DEFAULT_MAX_SECTION_LINES, help="warn above this many lines per section (default %d)" % DEFAULT_MAX_SECTION_LINES)
    ap.add_argument("--instrumental", action="store_true", help="do not require a chorus")
    ap.add_argument("--strict", action="store_true", help="exit 1 on warnings too")
    ap.add_argument("--json", action="store_true", help="print JSON")
    ap.add_argument("--version", action="version", version=__version__)
    a = ap.parse_args(argv)
    lyrics = sys.stdin.read() if a.lyrics == "-" else open(a.lyrics, encoding="utf-8").read()
    style = None
    if a.style:
        style = open(a.style, encoding="utf-8").read()
    elif a.style_text is not None:
        style = a.style_text
    issues = lint(lyrics, style, a.max_style, a.max_lyrics, a.max_section_lines, a.instrumental)
    if a.json:
        print(json.dumps({"file": a.lyrics, "issues": issues, "summary": summarise(issues)}, ensure_ascii=False, indent=2))
    else:
        print(format_text(issues, a.lyrics))
    c = summarise(issues)
    return 1 if c["error"] or (a.strict and c["warn"]) else 0


if __name__ == "__main__":
    sys.exit(main())
