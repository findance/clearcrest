"""Validated linear-chain state and UTXO application."""
from clearcrest.consensus.params import COINBASE_MATURITY, block_reward
from clearcrest.consensus.pow import valid_pow
from clearcrest.consensus.validation import validate_transaction
from clearcrest.core.block import Block
from clearcrest.storage.database import ChainDatabase

class Blockchain:
    def __init__(self, database: ChainDatabase | None = None):
        self.db = database or ChainDatabase()
        self.tip = b"\0" * 32
    @property
    def height(self) -> int: return self.db.height()
    def add_block(self, block: Block) -> int:
        height = self.height + 1
        if block.header.prev_hash != self.tip or not block.validate_merkle() or not valid_pow(block.header.serialize(), block.header.target): raise ValueError("invalid block header")
        if not block.transactions or block.transactions[0].tx_type.name != "COINBASE": raise ValueError("block must start with coinbase")
        available = {(txid, index): amount for txid, index, amount, _, _, _ in self.db.utxos()}
        with self.db.connection:
            for pos, tx in enumerate(block.transactions):
                if pos == 0:
                    if tx.outputs[0].amount != block_reward(height): raise ValueError("incorrect block reward")
                    validate_transaction(tx, available, 0)
                else:
                    validate_transaction(tx, available, 250)
                    for point in tx.spent_outpoints(): self.db.spend(*point); available.pop(point)
                for index, output in enumerate(tx.outputs):
                    self.db.put_utxo(tx.txid, index, output.amount, output.recipient, height, pos == 0)
                    available[(tx.txid, index)] = output.amount
            self.db.save_block(height, block.header.hash, self.tip, block.serialize())
        self.tip = block.header.hash
        return height
    def get_balance(self, recipient: bytes, at_height: int | None = None) -> int:
        height = self.height if at_height is None else at_height
        return sum(amount for _, _, amount, _, created, coinbase in self.db.utxos(recipient) if not coinbase or height >= created + COINBASE_MATURITY)

