"""Fail-closed signature provider boundary.

ClearCrest does not provide a home-grown post-quantum signature implementation.
A deployment must register a reviewed FIPS 204/205 provider before signing or
verification is possible.
"""
from dataclasses import dataclass
from typing import Protocol

ML_DSA_65 = 0x01
SLH_DSA = 0x02

class SignatureProvider(Protocol):
    version: int
    def generate_keypair(self) -> tuple[bytes, bytes]: ...
    def sign(self, private_key: bytes, message: bytes) -> bytes: ...
    def verify(self, public_key: bytes, message: bytes, signature: bytes) -> bool: ...

@dataclass
class KeyRegistry:
    _providers: dict[int, SignatureProvider]
    def register(self, provider: SignatureProvider) -> None:
        if provider.version not in (ML_DSA_65, SLH_DSA): raise ValueError("unsupported key version")
        self._providers[provider.version] = provider
    def provider(self, version: int) -> SignatureProvider:
        try: return self._providers[version]
        except KeyError: raise RuntimeError("no reviewed signature provider registered") from None
    def generate_keypair(self, version: int = ML_DSA_65) -> tuple[bytes, bytes]:
        return self.provider(version).generate_keypair()
    def verify(self, version: int, public_key: bytes, message: bytes, signature: bytes) -> bool:
        return self.provider(version).verify(public_key, message, signature)

registry = KeyRegistry({})

