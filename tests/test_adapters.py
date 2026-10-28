"""Structure checks shared by every uniqaiapp repo: SKILL.md frontmatter, adapters point at it,
versions agree, and no file contains a forbidden string (personal names, local paths, secrets)."""
import json
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = "suno-producer"
TEXT_EXT = {".md", ".py", ".json", ".yml", ".yaml", ".txt", ".mdc", ".svg", ".cff", ".toml", ".cfg", ""}
SKIP_DIRS = {".git", "__pycache__"}
# Built by concatenation so this file does not trip its own scan.
FORBIDDEN = [
    "aeo" + "ria", "rich" + "peach", "/Use" + "rs/", "/Volu" + "mes/", "node_" + "modules",
    "sk-" + "ant-", "sk_" + "live", "api_" + "key=", "API_" + "KEY=<real", "TODO: " + "fill", "lorem " + "ipsum",
]
EXEMPT = {".gitignore": ["node_" + "modules"]}


def read(rel):
    with open(os.path.join(ROOT, rel), encoding="utf-8") as fh:
        return fh.read()


def frontmatter(text):
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    assert m, "no frontmatter"
    out = {}
    stack = [(-1, out)]
    for line in m.group(1).splitlines():
        if not line.strip():
            continue
        indent = len(line) - len(line.lstrip())
        key, _, val = line.strip().partition(":")
        while stack and stack[-1][0] >= indent:
            stack.pop()
        parent = stack[-1][1]
        if val.strip() == "":
            parent[key] = {}
            stack.append((indent, parent[key]))
        else:
            parent[key] = val.strip()
    return out


def tracked_files():
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for f in filenames:
            p = os.path.join(dirpath, f)
            if os.path.splitext(f)[1].lower() in TEXT_EXT:
                yield os.path.relpath(p, ROOT)


class Skill(unittest.TestCase):
    def setUp(self):
        self.fm = frontmatter(read("SKILL.md"))

    def test_name_matches_repo(self):
        self.assertEqual(self.fm["name"], REPO)
        self.assertRegex(self.fm["name"], r"^[a-z0-9-]{1,64}$")

    def test_description(self):
        d = self.fm["description"]
        self.assertTrue(1 <= len(d) <= 1024, len(d))
        self.assertNotIn("\n", d)
        for phrase in ("Suno", "Use when", "Not for", "Suno prompt"):
            self.assertIn(phrase, d)

    def test_body_length(self):
        self.assertLess(len(read("SKILL.md").splitlines()), 500)

    def test_referenced_files_exist(self):
        body = read("SKILL.md")
        for rel in set(re.findall(r"`((?:scripts|references|examples)/[\w./-]+)`", body)):
            self.assertTrue(os.path.exists(os.path.join(ROOT, rel)), rel)


class Adapters(unittest.TestCase):
    def test_plugin_json(self):
        fm = frontmatter(read("SKILL.md"))
        plugin = json.loads(read(".claude-plugin/plugin.json"))
        self.assertEqual(plugin["name"], fm["name"])
        self.assertEqual(plugin["version"], fm["metadata"]["version"])
        self.assertEqual(plugin["author"]["name"], "UniqAI")
        self.assertEqual(plugin["skills"], ["./"])

    def test_cursor_rule(self):
        mdc = read(".cursor/rules/%s.mdc" % REPO)
        self.assertIn("@SKILL.md", mdc)
        self.assertTrue(mdc.startswith("---\n"))

    def test_agents_and_codex_mention_skill(self):
        self.assertIn("SKILL.md", read("AGENTS.md"))
        self.assertIn("SKILL.md", read("codex/INSTRUCTIONS.md"))

    def test_changelog_version(self):
        fm = frontmatter(read("SKILL.md"))
        m = re.search(r"^## \[(\d+\.\d+\.\d+)\] - \d{4}-\d{2}-\d{2}", read("CHANGELOG.md"), re.M)
        self.assertIsNotNone(m)
        self.assertEqual(m.group(1), fm["metadata"]["version"])

    def test_repo_json(self):
        meta = json.loads(read(".github/repo.json"))
        self.assertEqual(meta["name"], REPO)
        self.assertLessEqual(len(meta["topics"]), 20)
        self.assertIn("utm_campaign=" + REPO, meta["homepage"])

    def test_required_files(self):
        for rel in ("README.md", "README.ru.md", "LICENSE", "CONTRIBUTING.md", "CHANGELOG.md", "AGENTS.md",
                    ".github/workflows/ci.yml", ".github/ISSUE_TEMPLATE/bug_report.md",
                    ".github/ISSUE_TEMPLATE/feature_request.md", ".github/ISSUE_TEMPLATE/config.yml",
                    ".github/PULL_REQUEST_TEMPLATE.md", "assets/banner.svg", "assets/banner-light.svg",
                    "assets/demo.svg", "assets/social-preview.png", "assets/icon.svg", "examples/README.md"):
            self.assertTrue(os.path.exists(os.path.join(ROOT, rel)), rel)


class Readme(unittest.TestCase):
    def test_utm_on_every_uniqai_link(self):
        for rel in ("README.md", "README.ru.md"):
            text = read(rel)
            links = re.findall(r"https://uniqai\.app[^\s)\"'>]*", text)
            self.assertTrue(links, rel)
            for link in links:
                self.assertIn("utm_source=github", link, rel + " " + link)
                self.assertIn("utm_campaign=" + REPO, link, rel + " " + link)
            self.assertLessEqual(len(links), 3, rel)

    def test_one_made_by_footer(self):
        self.assertEqual(read("README.md").count("Made by <a href"), 1)


class Forbidden(unittest.TestCase):
    def test_no_forbidden_strings(self):
        hits = []
        for rel in tracked_files():
            try:
                text = read(rel).lower()
            except UnicodeDecodeError:
                continue
            exempt = EXEMPT.get(os.path.basename(rel), [])
            for s in FORBIDDEN:
                if s.lower() in text and s not in exempt and "conventions-allow: abs-path" not in text:
                    hits.append("%s: %s" % (rel, s))
        self.assertEqual(hits, [])

    def test_copyright_lines_are_brand_only(self):
        for rel in tracked_files():
            try:
                text = read(rel)
            except UnicodeDecodeError:
                continue
            marker = "Copyright " + "(c)"
            for line in text.splitlines():
                if marker in line:
                    self.assertIn("UniqAI", line, rel)


if __name__ == "__main__":
    unittest.main()
