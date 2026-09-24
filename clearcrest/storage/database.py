"""Small transactional SQLite persistence layer."""
import sqlite3
from pathlib import Path

class ChainDatabase:
    def __init__(self, path: str | Path = ":memory:"):
        self.connection = sqlite3.connect(path)
        self.connection.execute("PRAGMA foreign_keys = ON")
        self.connection.executescript("""
            CREATE TABLE IF NOT EXISTS blocks (height INTEGER PRIMARY KEY, hash BLOB UNIQUE NOT NULL, prev_hash BLOB NOT NULL, payload BLOB NOT NULL);
            CREATE TABLE IF NOT EXISTS utxos (txid BLOB NOT NULL, output_index INTEGER NOT NULL, amount INTEGER NOT NULL, recipient BLOB NOT NULL, height INTEGER NOT NULL, coinbase INTEGER NOT NULL, PRIMARY KEY(txid, output_index));
            CREATE TABLE IF NOT EXISTS filters (height INTEGER PRIMARY KEY, filter BLOB NOT NULL, filter_hash BLOB NOT NULL);
            CREATE TABLE IF NOT EXISTS channels (channel_id BLOB PRIMARY KEY, state BLOB NOT NULL);
            CREATE INDEX IF NOT EXISTS utxos_recipient ON utxos(recipient);
        """)
    def save_block(self, height: int, block_hash: bytes, prev_hash: bytes, payload: bytes) -> None:
        with self.connection: self.connection.execute("INSERT INTO blocks VALUES (?, ?, ?, ?)", (height, block_hash, prev_hash, payload))
    def height(self) -> int: return self.connection.execute("SELECT COALESCE(MAX(height), -1) FROM blocks").fetchone()[0]
    def put_utxo(self, txid: bytes, index: int, amount: int, recipient: bytes, height: int, coinbase: bool) -> None:
        self.connection.execute("INSERT INTO utxos VALUES (?, ?, ?, ?, ?, ?)", (txid, index, amount, recipient, height, int(coinbase)))
    def spend(self, txid: bytes, index: int) -> None:
        if self.connection.execute("DELETE FROM utxos WHERE txid=? AND output_index=?", (txid, index)).rowcount != 1: raise ValueError("UTXO missing")
    def utxos(self, recipient: bytes | None = None):
        sql = "SELECT txid, output_index, amount, recipient, height, coinbase FROM utxos" + (" WHERE recipient=?" if recipient is not None else "")
        return self.connection.execute(sql, (() if recipient is None else (recipient,))).fetchall()
    def prune(self, retain_from: int) -> int:
        with self.connection:
            return self.connection.execute("DELETE FROM blocks WHERE height < ?", (retain_from,)).rowcount

