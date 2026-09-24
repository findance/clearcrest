"""Deterministic compact membership filter.

This is a protocol-local Golomb-Rice encoder with a SHA3 keyed mapping. It is not
wire-compatible with BIP158, but has the same false-positive-only matching contract.
"""
from bisect import bisect_left
from clearcrest.crypto.hashing import sha3_256

P = 19
M = 784_931

def _bits(values: list[int]) -> bytes:
    out = bytearray(); acc = used = 0
    for value, width in values:
        acc = (acc << width) | value; used += width
        while used >= 8:
            used -= 8; out.append((acc >> used) & 255)
    if used: out.append((acc << (8 - used)) & 255)
    return bytes(out)

def _map(key: bytes, item: bytes, n: int) -> int:
    return int.from_bytes(sha3_256(key + item)[:8], "big") % max(1, n * M)

def build_gcs_filter(items: list[bytes], key: bytes) -> bytes:
    if len(key) != 32: raise ValueError("filter key must be 32 bytes")
    mapped = sorted({_map(key, item, len(items)) for item in items})
    encoded: list[tuple[int, int]] = []; previous = 0
    for value in mapped:
        delta = value - previous; previous = value
        encoded.extend([(1, 1)] * (delta >> P)); encoded.append((0, 1)); encoded.append((delta & ((1 << P) - 1), P))
    return len(mapped).to_bytes(4, "big") + _bits(encoded)

def filter_hash(filter_bytes: bytes) -> bytes: return sha3_256(filter_bytes)

def match_filter(filter_bytes: bytes, key: bytes, items: list[bytes]) -> bool:
    count = int.from_bytes(filter_bytes[:4], "big"); data = filter_bytes[4:]
    bits = "".join(f"{byte:08b}" for byte in data); pos = 0; current = 0; values = []
    try:
        for _ in range(count):
            quotient = 0
            while bits[pos] == "1": quotient += 1; pos += 1
            pos += 1; remainder = int(bits[pos:pos + P], 2); pos += P
            current += (quotient << P) | remainder; values.append(current)
    except (IndexError, ValueError): raise ValueError("malformed compact filter")
    return any((index := bisect_left(values, _map(key, item, count))) < len(values) and values[index] == _map(key, item, count) for item in items)

