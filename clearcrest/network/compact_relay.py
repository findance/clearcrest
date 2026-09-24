"""Compact relay reconstruction using collision-resistant short identifiers."""
from dataclasses import dataclass
from clearcrest.crypto.hashing import sha3_256
from clearcrest.core.block import Block, BlockHeader
from clearcrest.core.transaction import Transaction

def short_id(key: bytes, txid: bytes) -> bytes: return sha3_256(key + txid)[:8]

@dataclass(frozen=True)
class CompactBlock:
    header: BlockHeader
    key: bytes
    short_ids: tuple[bytes, ...]
    prefilled: tuple[tuple[int, Transaction], ...] = ()

    @classmethod
    def from_block(cls, block: Block, key: bytes, prefilled_indexes: set[int] | None = None):
        indexes = prefilled_indexes or {0}
        return cls(block.header, key, tuple(short_id(key, tx.txid) for i, tx in enumerate(block.transactions) if i not in indexes), tuple((i, tx) for i, tx in enumerate(block.transactions) if i in indexes))

def request_missing(compact: CompactBlock, mempool: dict[bytes, Transaction]) -> list[bytes]:
    known = {short_id(compact.key, txid): txid for txid in mempool}
    return [sid for sid in compact.short_ids if sid not in known]

def reconstruct_block(compact: CompactBlock, mempool: dict[bytes, Transaction]) -> Block:
    by_short = {short_id(compact.key, txid): tx for txid, tx in mempool.items()}
    if request_missing(compact, mempool): raise ValueError("missing compact-block transactions")
    total = len(compact.short_ids) + len(compact.prefilled); values: list[Transaction | None] = [None] * total
    for index, tx in compact.prefilled: values[index] = tx
    iterator = iter(compact.short_ids)
    for index in range(total):
        if values[index] is None: values[index] = by_short[next(iterator)]
    return Block(compact.header, tuple(values))

