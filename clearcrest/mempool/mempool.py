from clearcrest.consensus.params import MIN_FEE
from clearcrest.core.transaction import Transaction

class Mempool:
    def __init__(self) -> None:
        self.transactions: dict[bytes, tuple[Transaction, int]] = {}
        self._outpoints: dict[tuple[bytes, int], bytes] = {}
    def add(self, tx: Transaction, fee: int) -> bytes:
        if fee < MIN_FEE: raise ValueError("fee below minimum")
        conflicts = {self._outpoints[p] for p in tx.spent_outpoints() if p in self._outpoints}
        if conflicts:
            if len(conflicts) != 1 or not tx.rbf: raise ValueError("conflicting transaction")
            oldid = conflicts.pop(); oldtx, oldfee = self.transactions[oldid]
            if not oldtx.rbf or fee <= oldfee: raise ValueError("RBF fee must be strictly higher")
            if oldtx.spent_outpoints() != tx.spent_outpoints(): raise ValueError("RBF must spend identical inputs")
            self.remove(oldid)
        txid = tx.txid; self.transactions[txid] = (tx, fee)
        for point in tx.spent_outpoints(): self._outpoints[point] = txid
        return txid
    def remove(self, txid: bytes) -> None:
        record = self.transactions.pop(txid, None)
        if record:
            for point in record[0].spent_outpoints(): self._outpoints.pop(point, None)
    def ordered(self) -> list[Transaction]:
        return [x[0] for x in sorted(self.transactions.values(), key=lambda x: x[1], reverse=True)]

