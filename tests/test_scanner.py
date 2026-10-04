"""Tests for scanner module."""

import tempfile
import unittest
from pathlib import Path
from capcut_cache_recover.scanner import is_bdve_file, find_encrypted_videos


class TestScanner(unittest.TestCase):
    def test_non_bdve_file(self):
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
            tmp.write(b"\x00" * 100)
            tmp_path = Path(tmp.name)

        try:
            self.assertFalse(is_bdve_file(tmp_path))
        finally:
            tmp_path.unlink(missing_ok=True)

    def test_synthetic_bdve_detection(self):
        crpt_sha = b"\xbb" * 32
        crpt_payload = (
            (1).to_bytes(4, "big") +
            (3).to_bytes(4, "big") +
            crpt_sha
        )
        crpt_box = (8 + len(crpt_payload)).to_bytes(4, "big") + b"crpt" + crpt_payload
        size_box = (12).to_bytes(4, "big") + b"size" + (68).to_bytes(4, "big")
        bdve_box = (68).to_bytes(4, "big") + b"bdve" + crpt_box + size_box

        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
            tmp.write(b"data" * 50 + bdve_box)
            tmp_path = Path(tmp.name)

        try:
            self.assertTrue(is_bdve_file(tmp_path))
            found = list(find_encrypted_videos(tmp_path.parent))
            self.assertIn(tmp_path, found)
        finally:
            tmp_path.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
