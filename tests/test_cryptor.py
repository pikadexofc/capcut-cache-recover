"""Tests for capcut_cache_recover cryptor module."""

import hashlib
import unittest
from capcut_cache_recover.cryptor import (
    xor_bytes,
    param_sha256,
    parse_bdve_footer,
    BdveFooter,
    iter_boxes,
)


class TestCryptor(unittest.TestCase):
    def test_xor_bytes(self):
        data = b"Hello, World!"
        key = 0x3B
        xored = xor_bytes(data, key)
        self.assertNotEqual(data, xored)
        restored = xor_bytes(xored, key)
        self.assertEqual(data, restored)

    def test_param_sha256(self):
        step = 49435
        length = 18115
        key = 0x3B
        expected = hashlib.sha256(
            step.to_bytes(4, "big") + length.to_bytes(4, "big") + bytes([key])
        ).digest()
        self.assertEqual(param_sha256(step, length, key), expected)

    def test_parse_bdve_footer(self):
        # Construct synthetic BDVE footer
        # bdve box: 4 bytes size, 4 bytes 'bdve', child crpt box, size box at end
        crpt_sha = b"\xaa" * 32
        crpt_payload = (
            (1).to_bytes(4, "big") +  # cryptor_type = 1
            (3).to_bytes(4, "big") +  # version = 3
            crpt_sha
        )
        crpt_box = (8 + len(crpt_payload)).to_bytes(4, "big") + b"crpt" + crpt_payload
        size_box = (12).to_bytes(4, "big") + b"size" + (68).to_bytes(4, "big")
        bdve_box = (68).to_bytes(4, "big") + b"bdve" + crpt_box + size_box

        footer = parse_bdve_footer(bdve_box)
        self.assertIsNotNone(footer)
        self.assertEqual(footer.size, 68)
        self.assertEqual(footer.cryptor_type, 1)
        self.assertEqual(footer.version, 3)
        self.assertEqual(footer.sha256, crpt_sha)

    def test_iter_boxes(self):
        synthetic = (
            (16).to_bytes(4, "big") + b"ftyp" + b"isom" + (512).to_bytes(4, "big") +
            (12).to_bytes(4, "big") + b"free" + b"junk"
        )
        boxes = list(iter_boxes(synthetic, 0, len(synthetic)))
        self.assertEqual(len(boxes), 2)
        self.assertEqual(boxes[0].type, b"ftyp")
        self.assertEqual(boxes[0].size, 16)
        self.assertEqual(boxes[1].type, b"free")
        self.assertEqual(boxes[1].size, 12)


if __name__ == "__main__":
    unittest.main()
