"""Keep the copied official implementation exact and attributable."""
import hashlib
import json
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[1]/"contributions/template-system-keys"
class SystemKeysTests(unittest.TestCase):
 def test_official_sources_remain_unchanged(self):
  manifest=json.loads((ROOT/"upstream.json").read_text())
  self.assertEqual(len(manifest["commit"]),40)
  for item in manifest["files"]:
   self.assertEqual(hashlib.sha256((ROOT/"upstream"/Path(item["path"]).name).read_bytes()).hexdigest(),item["sha256"])
  self.assertIn("MIT",(ROOT/"LICENSE").read_text())
