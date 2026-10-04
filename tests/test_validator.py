"""Tests for MP4 validator module."""

import tempfile
import unittest
from pathlib import Path
from capcut_cache_recover.validator import validate_mp4


class TestValidator(unittest.TestCase):
    def test_non_existent_file(self):
        res = validate_mp4(Path("non_existent_file.mp4"))
        self.assertFalse(res.is_valid)
        self.assertIn("does not exist", res.error)

    def test_empty_file(self):
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
            tmp.write(b"")
            tmp_path = Path(tmp.name)

        try:
            res = validate_mp4(tmp_path)
            self.assertFalse(res.is_valid)
            self.assertIn("too small", res.error)
        finally:
            tmp_path.unlink(missing_ok=True)

    def test_recovered_video_validation(self):
        # Validate against the recovered desktop video if available
        desktop_video = Path(r"C:\Users\Shanto\Desktop\shining_motion_u_recovered.mp4")
        if desktop_video.exists():
            res = validate_mp4(desktop_video)
            self.assertTrue(res.is_valid)
            self.assertTrue(res.has_video)
            self.assertTrue(res.has_audio)
            self.assertGreater(res.duration_seconds, 20.0)
            self.assertEqual(res.video_width, 1080)
            self.assertEqual(res.video_height, 1920)


if __name__ == "__main__":
    unittest.main()
