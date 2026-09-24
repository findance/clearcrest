"""Minimal Bech32m address codec (BIP-350 checksum constant)."""
from .hashing import hash160

HRP = "cc"
BECH32M_CONST = 0x2BC830A3
CHARSET = "qpzry9x8gf2tvdw0s3jn54khce6mua7l"
CHARSET_REV = {char: pos for pos, char in enumerate(CHARSET)}
SUPPORTED_VERSIONS = {1, 2}

def _polymod(values: list[int]) -> int:
    chk = 1
    for value in values:
        top = chk >> 25
        chk = (chk & 0x1FFFFFF) << 5 ^ value
        for index, generator in enumerate((0x3B6A57B2, 0x26508E6D, 0x1EA119FA, 0x3D4233DD, 0x2A1462B3)):
            if (top >> index) & 1: chk ^= generator
    return chk

def _expand_hrp(hrp: str) -> list[int]:
    return [ord(x) >> 5 for x in hrp] + [0] + [ord(x) & 31 for x in hrp]

def _checksum(hrp: str, data: list[int]) -> list[int]:
    value = _polymod(_expand_hrp(hrp) + data + [0] * 6) ^ BECH32M_CONST
    return [(value >> 5 * (5 - i)) & 31 for i in range(6)]

def _convertbits(data: bytes, frombits: int = 8, tobits: int = 5) -> list[int]:
    acc = bits = 0; result: list[int] = []
    for byte in data:
        acc = (acc << frombits) | byte; bits += frombits
        while bits >= tobits:
            bits -= tobits; result.append((acc >> bits) & ((1 << tobits) - 1))
    if bits: result.append((acc << (tobits - bits)) & ((1 << tobits) - 1))
    return result

def pubkey_to_address(public_key: bytes, version: int = 1) -> str:
    if version not in SUPPORTED_VERSIONS: raise ValueError("unsupported key version")
    data = [version] + _convertbits(hash160(public_key))
    return HRP + "1" + "".join(CHARSET[x] for x in data + _checksum(HRP, data))

def validate_address(address: str) -> bool:
    if address.lower() != address or not address.startswith(HRP + "1") or len(address) > 90: return False
    try: data = [CHARSET_REV[x] for x in address[len(HRP) + 1:]]
    except KeyError: return False
    return len(data) >= 7 and data[0] in SUPPORTED_VERSIONS and _polymod(_expand_hrp(HRP) + data) == BECH32M_CONST

