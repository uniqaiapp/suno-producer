import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import suno_lint as sl  # noqa: E402


def rules(issues, level=None):
    return sorted({i["rule"] for i in issues if level is None or i["level"] == level})


class LintRules(unittest.TestCase):
    def test_clean(self):
        text = "[Intro]\n\n[Verse 1]\nfirst line\nsecond line\n\n[Chorus]\nhook line\nhook line\n\n[Outro]\nhook line\n"
        issues = sl.lint(text, "indie pop, 110 BPM, warm female vocal")
        self.assertEqual(rules(issues, "error"), [])
        self.assertEqual(rules(issues, "warn"), [])

    def test_untagged_and_missing_chorus(self):
        issues = sl.lint("just some words\nmore words\n")
        self.assertIn("L002", rules(issues))
        issues = sl.lint("[Verse]\nwords\n")
        self.assertIn("L003", rules(issues))
        self.assertNotIn("L003", rules(sl.lint("[Verse]\nwords\n", instrumental=True)))

    def test_tags(self):
        issues = sl.lint("[verse]\nwords\n[Chorus]\nwords\n")
        self.assertIn("L014", rules(issues))
        issues = sl.lint("[Verse]\nwords\n[Kazoo Frenzy]\nwords\n[Chorus]\nwords\n")
        self.assertIn("L001", rules(issues))
        issues = sl.lint("[Chorus]\n[Chorus]\nwords\n")
        self.assertIn("L004", rules(issues))
        issues = sl.lint("[Verse]\n[Chorus]\nwords\n")
        self.assertIn("L016", rules(issues))
        self.assertNotIn("L016", rules(sl.lint("[Intro]\n[Chorus]\nwords\n")))
        issues = sl.lint("[Chorus] words on the tag line\nmore\n")
        self.assertIn("L010", rules(issues))
        issues = sl.lint("[Verse]\nwords\n[Outro]\nbye\n[Chorus]\nwords\n")
        self.assertIn("L005", rules(issues))

    def test_brackets_and_imitation(self):
        issues = sl.lint("[Chorus\nwords\n")
        self.assertIn("L006", rules(issues, "error"))
        issues = sl.lint("[Chorus]\nI want this in the style of a star\n")
        self.assertIn("L007", rules(issues, "error"))
        issues = sl.lint("[Chorus]\nfine\n", "pop, sounds like a famous band")
        self.assertIn("L007", rules(issues, "error"))
        issues = sl.lint("[Chorus]\nfine\n", "поп, в стиле известной группы")
        self.assertIn("L007", rules(issues, "error"))

    def test_budgets(self):
        issues = sl.lint("[Chorus]\n" + "x" * 50 + "\n", "a" * 30, max_style=20, max_lyrics=40)
        self.assertIn("L008", rules(issues, "error"))
        self.assertIn("L009", rules(issues, "error"))
        issues = sl.lint("[Chorus]\n" + "line\n" * 5, max_section_lines=4)
        self.assertIn("L011", rules(issues))

    def test_style_shape(self):
        issues = sl.lint("[Chorus]\nfine\n", "[Chorus] pop\nline\nline\nline")
        self.assertIn("L012", rules(issues))
        self.assertIn("L013", rules(issues))
        self.assertIn("L015", rules(issues, "info"))
        issues = sl.lint("[Chorus]\nfine\n", "")
        self.assertIn("L008", rules(issues, "warn"))

    def test_base_tag(self):
        self.assertEqual(sl.base_tag("Verse 2"), "verse")
        self.assertEqual(sl.base_tag("Pre-Chorus"), "pre-chorus")
        self.assertEqual(sl.base_tag("Chorus: big"), "chorus")
        self.assertEqual(sl.base_tag("Guitar Solo (short)"), "guitar solo")


if __name__ == "__main__":
    unittest.main()
