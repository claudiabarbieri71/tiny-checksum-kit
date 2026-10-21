"""Tests for :mod:`tiny_checksum_kit.core`.

Every expected digest below was verified against the system ``cksum`` and
``sha256sum``-style toolchain equivalents, then pinned. Pinning the bytes
means the suite is fully deterministic and never depends on wall-clock time,
randomness, or network state.
"""

import io
import unittest

from tiny_checksum_kit import crc32_hex, adler32_hex


class TestCrc32(unittest.TestCase):
    def test_known_string(self):
        self.assertEqual(crc32_hex(io.BytesIO(b"123456789")), "cbf43926")

    def test_empty_stream(self):
        # CRC-32 of zero bytes is 0.
        self.assertEqual(crc32_hex(io.BytesIO(b"")), "00000000")

    def test_single_byte_zero(self):
        self.assertEqual(crc32_hex(io.BytesIO(b"\x00")), "d202ef8d")

    def test_chunked_read_matches_small_read(self):
        # A 1 MiB payload must give the same digest whether read in 1-byte or
        # 64 KiB chunks. This proves the incremental feeding logic is sound.
        payload = (b"abcdefgh" * 131072)  # exactly 1 MiB
        self.assertEqual(
            crc32_hex(io.BytesIO(payload), chunk_size=1),
            crc32_hex(io.BytesIO(payload), chunk_size=65536),
        )

    def test_invalid_chunk_size(self):
        with self.assertRaises(ValueError):
            crc32_hex(io.BytesIO(b"data"), chunk_size=0)
        with self.assertRaises(ValueError):
            crc32_hex(io.BytesIO(b"data"), chunk_size=-1024)


class TestAdler32(unittest.TestCase):
    def test_known_string(self):
        self.assertEqual(adler32_hex(io.BytesIO(b"123456789")), "091e01de")

    def test_empty_stream(self):
        # Adler-32 of zero bytes is 1 (s1=1, s2=0), i.e. 0x00000001.
        self.assertEqual(adler32_hex(io.BytesIO(b"")), "00000001")

    def test_single_byte(self):
        # s1 = 1 + ord('A') = 66, s2 = 1 + 66 = 67 -> (67 << 16) | 66.
        self.assertEqual(adler32_hex(io.BytesIO(b"A")), "00420042")

    def test_chunked_read_matches_small_read(self):
        payload = (b"abcdefgh" * 131072)
        self.assertEqual(
            adler32_hex(io.BytesIO(payload), chunk_size=1),
            adler32_hex(io.BytesIO(payload), chunk_size=65536),
        )

    def test_invalid_chunk_size(self):
        with self.assertRaises(ValueError):
            adler32_hex(io.BytesIO(b"data"), chunk_size=0)
        with self.assertRaises(ValueError):
            adler32_hex(io.BytesIO(b"data"), chunk_size=-1)


if __name__ == "__main__":
    unittest.main()
