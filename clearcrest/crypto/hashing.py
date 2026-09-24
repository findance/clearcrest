"""Hash functions used by the protocol."""
from hashlib import sha3_256 as _sha3_256

def sha3_256(data: bytes) -> bytes:
    return _sha3_256(data).digest()

def double_sha3(data: bytes) -> bytes:
    return sha3_256(sha3_256(data))

def hash160(data: bytes) -> bytes:
    """ClearCrest's 20-byte address identifier (SHA3-256 truncated)."""
    return sha3_256(data)[:20]

