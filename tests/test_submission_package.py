# SPDX-License-Identifier: MIT
"""Keep review packages tied to tested source without exporting raw device data."""
import copy
import importlib.util
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
SPEC=importlib.util.spec_from_file_location("submission_package",ROOT/"submissions/m5stack-2026-11-16/build_package.py")
PACKAGE=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(PACKAGE)


class SubmissionPackageTests(unittest.TestCase):
    def setUp(self):
        self.meta={"mesh_commit":"a"*40,"template_commit":"b"*40,"mesh_version":"0.1.11","template_patch_sha256":"c"*64}
        self.proposal={"patch_sha256":"c"*64}
        self.evidence={"reviewed_on":"2026-11-16","mesh_source":"a"*40,"template_baseline":"b"*40,
            "template_patch_sha256":"c"*64,"local":{"mesh_backend_cases":98,"mesh_macos_sanitizers":"passed",
            "mesh_debian_arm64_reader_sanitizers":"passed","mesh_debian_arm64_package_upgrade_firewall":"passed",
            "template_macos_sanitizers":"passed","template_arm64_clean_source_sanitizers":"passed"},
            "mesh_ci":{"run_id":1,"conclusion":"success"},"installed_mesh":{"status":"verified","version":"0.1.11",
            "package_sha256":"d"*64,**{key:True for key in ["runtime_files_match","settings_preserved","history_preserved",
            "live_version_verified","input_replay","native_ui_startup","ordinary_user","firewall_healthy"]}},
            "limits":["Physical Template checks remain separate"],"upstream_submission":"not submitted"}

    def test_valid_allowlisted_evidence_passes(self):
        PACKAGE.validate_evidence(self.meta,self.evidence,self.proposal)

    def test_incomplete_or_wrong_source_is_refused(self):
        for changed in ("source","ci","installed"):
            record=copy.deepcopy(self.evidence)
            if changed=="source":record["mesh_source"]="e"*40
            if changed=="ci":record["mesh_ci"]["conclusion"]="in_progress"
            if changed=="installed":record["installed_mesh"]["input_replay"]=1
            with self.subTest(changed=changed),self.assertRaises(ValueError):
                PACKAGE.validate_evidence(self.meta,record,self.proposal)

    def test_raw_device_fields_or_private_material_are_refused(self):
        for changed in ("raw_field","nested_field","private_value"):
            record=copy.deepcopy(self.evidence)
            if changed=="raw_field":record["raw_logs"]="synthetic sensitive sentinel"
            if changed=="nested_field":record["installed_mesh"]["channel_key"]="synthetic sensitive sentinel"
            if changed=="private_value":record["limits"].append("/Users/synthetic/private")
            with self.subTest(changed=changed),self.assertRaises(ValueError):
                PACKAGE.validate_evidence(self.meta,record,self.proposal)

    def test_complete_exact_source_ci_required(self):
        guide="f"*40
        snapshot={"guide_commit":guide,"mesh_commit":"a"*40,"template_patch_sha256":"c"*64,"runs":[]}
        for i,name in enumerate(["Guide and offline preflight","Prepared Template keyboard contribution","M5Stack review report","Offline regressions"]):
            repo="Prophet60191/m5stack-cardputer-zero-"+("mesh-app" if i==3 else "app-guide")
            snapshot["runs"].append({"repository":repo,"run_id":i+1,"name":name,
                "head_sha":"a"*40 if i==3 else guide,"conclusion":"success",
                "url":f"https://github.com/{repo}/actions/runs/{i+1}"})
        PACKAGE.validate_ci(snapshot,guide,self.meta)
        snapshot["runs"].pop()
        with self.assertRaises(ValueError):PACKAGE.validate_ci(snapshot,guide,self.meta)
        snapshot["template_patch_sha256"]="0"*64
        with self.assertRaises(ValueError):PACKAGE.validate_ci(snapshot,guide,self.meta)
