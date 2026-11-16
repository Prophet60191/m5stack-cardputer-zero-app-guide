# SPDX-License-Identifier: MIT
"""Guard proposal verification before any patch/build mutation happens."""
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("keyboard_verify", ROOT / "contributions/template-keyboard/verify.py")
VERIFY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VERIFY)


class KeyboardProposalTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.sources = [self.root / name for name in ("template", "lvgl")]
        for repo in self.sources:
            repo.mkdir()
            subprocess.run(["git", "init", "-q", str(repo)], check=True)
            (repo / "sentinel.txt").write_text("original\n")
            subprocess.run(["git", "-C", str(repo), "add", "sentinel.txt"], check=True)
            subprocess.run(["git", "-C", str(repo), "-c", "user.name=Synthetic",
                            "-c", "user.email=test@example.invalid", "commit", "-qm", "fixture"], check=True)
        self.meta = {key: VERIFY.run("git", "-C", str(repo), "rev-parse", "HEAD")
                     for key, repo in zip(("template_commit", "lvgl_commit"), self.sources)}
        self.patch_bytes = b"diff --git a/sentinel.txt b/sentinel.txt\n--- a/sentinel.txt\n+++ b/sentinel.txt\n@@ -1 +1 @@\n-original\n+proposed\n"
        self.meta["patch_sha256"] = hashlib.sha256(self.patch_bytes).hexdigest()
        (self.root / "keyboard.patch").write_bytes(self.patch_bytes)
        (self.root / "upstream.json").write_text(json.dumps(self.meta))
        self.override = patch.object(VERIFY, "ROOT", self.root)
        self.override.start()
        self.addCleanup(self.override.stop)

    def test_clean_check_does_not_apply_or_overwrite_source(self):
        VERIFY.checked_sources(*self.sources)
        self.assertEqual((self.sources[0] / "sentinel.txt").read_text(), "original\n")

    def test_dirty_source_is_refused_and_user_work_remains(self):
        (self.sources[0] / "sentinel.txt").write_text("user work\n")
        with self.assertRaisesRegex(ValueError, "clean source"):
            VERIFY.checked_sources(*self.sources)
        self.assertEqual((self.sources[0] / "sentinel.txt").read_text(), "user work\n")

    def test_changed_revision_or_patch_is_refused(self):
        self.meta["template_commit"] = "0" * 40
        (self.root / "upstream.json").write_text(json.dumps(self.meta))
        with self.assertRaisesRegex(ValueError, "reviewed revision"):
            VERIFY.checked_sources(*self.sources)
        (self.root / "keyboard.patch").write_bytes(self.patch_bytes + b"changed")
        with self.assertRaisesRegex(ValueError, "checksum"):
            VERIFY.checked_sources(*self.sources)

    def test_published_patch_matches_reviewed_metadata(self):
        source = ROOT / "contributions/template-keyboard"
        meta = json.loads((source / "upstream.json").read_text())
        self.assertEqual(hashlib.sha256((source / "keyboard.patch").read_bytes()).hexdigest(), meta["patch_sha256"])
        self.assertEqual(meta["template_commit"], "477fa6d217b683e3084c361a757f03dc8ca9f753")
        workflow = (ROOT / ".github/workflows/keyboard-proposal.yml").read_text()
        for key in ("template_commit", "lvgl_commit"):
            self.assertIn(meta[key], workflow)
