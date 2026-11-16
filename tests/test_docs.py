# SPDX-License-Identifier: MIT
"""Catch broken local links and policy-pin drift in the published instructions."""
import json
from pathlib import Path
import re
import unittest
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]


class DocumentationTests(unittest.TestCase):
    def test_local_markdown_links_and_anchors(self):
        for doc in [ROOT / "README.md", ROOT / "CHANGELOG.md", ROOT / "AGENTS.md",
                    *sorted((ROOT / "docs").rglob("*.md")),
                    *sorted((ROOT / "contributions").rglob("*.md")),
                    *sorted((ROOT / "submissions").rglob("*.md")), ROOT / "tools/README.md"]:
            text = doc.read_text(encoding="utf-8")
            for raw in re.findall(r"\]\(([^)]+)\)", text):
                if re.match(r"[a-zA-Z][a-zA-Z0-9+.-]*:", raw):
                    continue
                target, _, anchor = unquote(raw.strip("<>")).partition("#")
                path = doc.parent / target if target else doc
                with self.subTest(doc=doc.name, target=raw):
                    self.assertTrue(path.exists(), f"Missing local link: {raw}")
                    if anchor and path.suffix == ".md":
                        destination = path.read_text()
                        headings = re.findall(r"^#{1,6}\s+(.+?)\s*$", destination, re.M)
                        slugs = set(re.findall(r'<a\s+id="([^"]+)"', destination))
                        for h in headings:
                            h = re.sub(r"[^\w\- ]", "", h.lower()).replace(" ", "-")
                            slugs.add(h)
                        self.assertIn(anchor, slugs, f"Missing local heading: {raw}")

    def test_workflow_and_setup_use_reviewed_catalog_revision(self):
        lock = json.loads((ROOT / "tools/store-policy.lock.json").read_text())
        for name in [".github/workflows/check-guide.yml", "tools/README.md", "docs/store-readiness.md"]:
            self.assertIn(lock["packages_commit"], (ROOT / name).read_text())
        self.assertIn(lock["appbuilder_commit"], (ROOT / "docs/store-readiness.md").read_text())


if __name__ == "__main__":
    unittest.main()
