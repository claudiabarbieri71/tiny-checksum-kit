"""tiny-checksum-kit: CRC32 and Adler-32 for arbitrary streams.

Only the two checksum functions are part of the public API. Everything else
in :mod:`core` is an implementation detail kept private by the leading
underscore so callers cannot accidentally bind to it.
"""

from .core import crc32_hex, adler32_hex

__all__ = ["crc32_hex", "adler32_hex"]
