# tiny-checksum-kit

Streamed CRC-32 and Adler-32 digests for arbitrary binary streams, returned as lowercase hex strings.

```python
import io
from tiny_checksum_kit import crc32_hex, adler32_hex

data = io.BytesIO(b"the quick brown fox")
print(crc32_hex(data))    # -> 'bf3b668a'
data.seek(0)
print(adler32_hex(data))  # -> '1de40438'

with open(__file__, "rb") as f:
    print(crc32_hex(f, chunk_size=1 << 20))
```

## Why this exists

The standard library's `zlib` module already computes both digests correctly and quickly. What it does not give you is a convenient way to hash a file-backed stream without holding the whole file in memory, nor a stable string representation of the result. This library is a thin wrapper that reads a stream in fixed-size chunks and normalises the output to a zero-padded, lowercase hex string so digests can be compared directly across Python versions and platforms.

The trade-off is flexibility: only CRC-32 and Adler-32 are supported, and only as hex strings. If you need raw integers, a different algorithm, or a streaming `update()` interface, call `zlib` directly.

## Edge cases

An empty stream is valid and yields the algorithms' canonical zero-input digests: CRC-32 returns `00000000`, Adler-32 returns `00000001`. The `chunk_size` parameter must be a positive integer; passing zero or a negative value raises `ValueError` before any I/O is attempted.
