"""Byte-wise Shamir secret sharing over GF(256)."""
import secrets

def _mul(a: int, b: int) -> int:
    result = 0
    while b:
        if b & 1: result ^= a
        a <<= 1
        if a & 0x100: a ^= 0x11B
        b >>= 1
    return result

def _pow(a: int, n: int) -> int:
    result = 1
    while n:
        if n & 1: result = _mul(result, a)
        a = _mul(a, a); n >>= 1
    return result

def _div(a: int, b: int) -> int:
    if not b: raise ZeroDivisionError("GF(256) division by zero")
    return _mul(a, _pow(b, 254))

def _eval(coefficients: list[int], x: int) -> int:
    value = 0
    for coefficient in reversed(coefficients): value = _mul(value, x) ^ coefficient
    return value

def split_secret(secret: bytes, n: int, k: int) -> list[bytes]:
    if not secret or not 2 <= k <= n <= 255: raise ValueError("require non-empty secret and 2 <= k <= n <= 255")
    shares = [bytearray([i]) for i in range(1, n + 1)]
    for value in secret:
        coefficients = [value] + list(secrets.token_bytes(k - 1))
        for share in shares: share.append(_eval(coefficients, share[0]))
    return [bytes(share) for share in shares]

def recover_secret(shares: list[bytes]) -> bytes:
    if len(shares) < 2 or len({s[0] for s in shares}) != len(shares): raise ValueError("need distinct shares")
    length = len(shares[0])
    if length < 2 or any(len(s) != length for s in shares): raise ValueError("incompatible shares")
    result = bytearray()
    for offset in range(1, length):
        value = 0
        for share in shares:
            x, y = share[0], share[offset]; basis = 1
            for other in shares:
                if other is not share: basis = _mul(basis, _div(other[0], other[0] ^ x))
            value ^= _mul(y, basis)
        result.append(value)
    return bytes(result)

