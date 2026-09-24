"""Canonical transaction objects; signatures are validated by a supplied provider."""
from dataclasses import dataclass, field
from enum import IntEnum
from typing import Iterable
from clearcrest.crypto.hashing import double_sha3
from clearcrest.consensus.params import MAX_SUPPLY

class TxType(IntEnum):
    TRANSFER = 0x01
    COINBASE = 0x02
    CHANNEL_OPEN = 0x10
    CHANNEL_CLOSE = 0x11
    CHANNEL_FORCE_CLOSE = 0x12
    CHANNEL_PENALTY = 0x13
    CHANNEL_ANCHOR = 0x14
    HTLC_LOCK = 0x20
    HTLC_CLAIM = 0x21
    HTLC_REFUND = 0x22

def _u(value: int, width: int) -> bytes:
    if not 0 <= value < 1 << (width * 8): raise ValueError("integer out of range")
    return value.to_bytes(width, "big")

def _blob(value: bytes) -> bytes:
    return _u(len(value), 4) + value

@dataclass(frozen=True)
class TxInput:
    prev_txid: bytes
    output_index: int
    signature: bytes = b""
    public_key: bytes = b""
    def serialize(self) -> bytes:
        if len(self.prev_txid) != 32: raise ValueError("prev_txid must be 32 bytes")
        return self.prev_txid + _u(self.output_index, 4) + _blob(self.signature) + _blob(self.public_key)

@dataclass(frozen=True)
class TxOutput:
    amount: int
    recipient: bytes
    ephemeral_pubkey: bytes = b""
    def serialize(self) -> bytes:
        if not 0 <= self.amount <= MAX_SUPPLY: raise ValueError("invalid output amount")
        return _u(self.amount, 8) + _blob(self.recipient) + _blob(self.ephemeral_pubkey)

@dataclass(frozen=True)
class Transaction:
    tx_type: TxType
    inputs: tuple[TxInput, ...] = field(default_factory=tuple)
    outputs: tuple[TxOutput, ...] = field(default_factory=tuple)
    lock_height: int = 0
    lock_time: int = 0
    rbf: bool = False
    version: int = 1
    data: bytes = b""
    def __post_init__(self):
        object.__setattr__(self, "inputs", tuple(self.inputs)); object.__setattr__(self, "outputs", tuple(self.outputs))
    def serialize(self) -> bytes:
        parts = [_u(self.version, 2), _u(int(self.tx_type), 1), _u(self.lock_height, 8), _u(self.lock_time, 8), _u(int(self.rbf), 1), _u(len(self.inputs), 4)]
        parts.extend(txin.serialize() for txin in self.inputs)
        parts.append(_u(len(self.outputs), 4)); parts.extend(output.serialize() for output in self.outputs)
        parts.append(_blob(self.data)); return b"".join(parts)
    @property
    def txid(self) -> bytes: return double_sha3(self.serialize())
    def output_total(self) -> int: return sum(output.amount for output in self.outputs)
    def spent_outpoints(self) -> set[tuple[bytes, int]]: return {(item.prev_txid, item.output_index) for item in self.inputs}

def coinbase(height: int, amount: int, recipient: bytes) -> Transaction:
    if height < 0: raise ValueError("negative block height")
    return Transaction(TxType.COINBASE, outputs=(TxOutput(amount, recipient),), data=_u(height, 8))

