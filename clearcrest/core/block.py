"""Block structures with fixed-width header serialization."""
from dataclasses import dataclass, field
from clearcrest.consensus.params import MAX_BLOCK_SIZE
from clearcrest.crypto.hashing import double_sha3
from .merkle import merkle_root
from .transaction import Transaction

def _u(value: int, size: int) -> bytes:
    if not 0 <= value < 1 << (8 * size): raise ValueError("integer out of range")
    return value.to_bytes(size, "big")

@dataclass(frozen=True)
class BlockHeader:
    version: int
    prev_hash: bytes
    merkle_root: bytes
    filter_root: bytes
    timestamp: int
    target: int
    nonce: int = 0
    def serialize(self) -> bytes:
        if any(len(value) != 32 for value in (self.prev_hash, self.merkle_root, self.filter_root)): raise ValueError("hashes must be 32 bytes")
        return b"".join((_u(self.version, 4), self.prev_hash, self.merkle_root, self.filter_root, _u(self.timestamp, 8), _u(self.target, 32), _u(self.nonce, 8)))
    @property
    def hash(self) -> bytes: return double_sha3(self.serialize())

@dataclass(frozen=True)
class Block:
    header: BlockHeader
    transactions: tuple[Transaction, ...] = field(default_factory=tuple)
    def __post_init__(self): object.__setattr__(self, "transactions", tuple(self.transactions))
    def serialize(self) -> bytes:
        payload = self.header.serialize() + len(self.transactions).to_bytes(4, "big") + b"".join(tx.serialize() for tx in self.transactions)
        if len(payload) > MAX_BLOCK_SIZE: raise ValueError("block exceeds maximum size")
        return payload
    def validate_merkle(self) -> bool: return self.header.merkle_root == merkle_root([tx.txid for tx in self.transactions])

