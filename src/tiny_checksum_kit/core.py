"""Streaming CRC32 and Adler-32 built on :mod:`zlib`.

The Python standard library already implements both algorithms efficiently in
C via :func:`zlib.crc32` and :func:`zlib.adler32`. Re-implementing them in
pure Python would be both slower and an opportunity to introduce subtle
endian/sign bugs. We instead provide a thin, well-tested wrapper whose only
job is to feed an arbitrary binary stream to those functions in fixed-size
chunks and normalise the result to an unsigned, lowercase hex string.

Design decisions
----------------
* **Return hex strings, not ints.** The raw ``zlib`` functions return ints
  that can differ in *displayed* sign across Python versions and platforms
  even though the unsigned value is identical. A zero-padded, lowercase hex
  string removes that ambiguity and is directly comparable.
* **``chunk_size`` is a parameter, not a constant.** The sweet spot for
  throughput depends on storage media and available memory. We default to
  64 KiB, which is a safe choice for almost all local-disk workloads, but
  expose the knob so a caller on constrained hardware can shrink it.
* **The empty-stream case is valid.** Both algorithms define checksums for
  zero bytes (CRC32 -> ``'00000000'``, Adler-32 -> ``'00000001'``), so we
  return those rather than raising. This keeps the function a total mapping
  over readable streams.
"""

from __future__ import annotations

import zlib
from typing import IO, Iterable


__all__ = ["crc32_hex", "adler32_hex"]


def _iter_chunks(stream: IO[bytes], chunk_size: int) -> Iterable[bytes]:
    """Yield successive ``bytes`` chunks from ``stream``.

    A manual ``while True`` loop is used instead of ``iter(stream.read, b'')``
    because the latter silently masks :class:`OSError` raised on the first
    read as a normal end-of-stream, which would return a wrong checksum
    instead of propagating the failure.
    """
    while True:
        chunk = stream.read(chunk_size)
        if not chunk:
            break
        yield chunk


def crc32_hex(stream: IO[bytes], chunk_size: int = 65536) -> str:
    """Compute the CRC-32 of ``stream`` as an 8-character hex string.

    The stream is read in increments of ``chunk_size`` bytes and never held
    in memory in its entirety, so this is suitable for files larger than
    RAM.

    Parameters
    ----------
    stream:
        Any object exposing a ``read(n)`` method returning :class:`bytes`,
        e.g. a file opened in binary mode or :class:`io.BytesIO`.
    chunk_size:
        Number of bytes to read per iteration. Must be a positive integer.

    Returns
    -------
    str
        Lowercase, zero-padded, 8-character hexadecimal CRC-32 digest.

    Raises
    ------
    ValueError
        If ``chunk_size`` is not a positive integer.
    """
    if chunk_size <= 0:
        raise ValueError("chunk_size must be a positive integer")

    value = 0
    for chunk in _iter_chunks(stream, chunk_size):
        # Passing the running ``value`` as the second argument lets zlib
        # continue the digest across calls rather than restarting it.
        value = zlib.crc32(chunk, value)
    return f"{value & 0xFFFFFFFF:08x}"


def adler32_hex(stream: IO[bytes], chunk_size: int = 65536) -> str:
    """Compute the Adler-32 of ``stream`` as an 8-character hex string.

    The stream is read in increments of ``chunk_size`` bytes and never held
    in memory in its entirety.

    Parameters
    ----------
    stream:
        Any object exposing a ``read(n)`` method returning :class:`bytes`.
    chunk_size:
        Number of bytes to read per iteration. Must be a positive integer.

    Returns
    -------
    str
        Lowercase, zero-padded, 8-character hexadecimal Adler-32 digest.

    Raises
    ------
    ValueError
        If ``chunk_size`` is not a positive integer.
    """
    if chunk_size <= 0:
        raise ValueError("chunk_size must be a positive integer")

    value = 1
    for chunk in _iter_chunks(stream, chunk_size):
        value = zlib.adler32(chunk, value)
    return f"{value & 0xFFFFFFFF:08x}"
