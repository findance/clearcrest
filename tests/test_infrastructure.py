import unittest
from clearcrest.core.block import Block, BlockHeader
from clearcrest.core.filters import build_gcs_filter, match_filter
from clearcrest.core.merkle import merkle_root
from clearcrest.core.transaction import coinbase
from clearcrest.network.compact_relay import CompactBlock, reconstruct_block
from clearcrest.network.protocol import Message, decode_frame, encode_frame
from clearcrest.storage.database import ChainDatabase

class InfrastructureTests(unittest.TestCase):
    def test_block_and_compact_relay(self):
        tx = coinbase(0, 5_000_000_000, b"miner")
        header = BlockHeader(1, b"\0"*32, merkle_root([tx.txid]), b"\0"*32, 1, (1<<256)-1)
        block = Block(header, (tx,))
        compact = CompactBlock.from_block(block, b"k"*32)
        self.assertEqual(reconstruct_block(compact, {}), block)

    def test_filter_and_network_frame(self):
        encoded = build_gcs_filter([b"alice", b"bob"], b"k"*32)
        self.assertTrue(match_filter(encoded, b"k"*32, [b"alice"]))
        self.assertFalse(match_filter(encoded, b"k"*32, [b"carol"]))
        message = Message("ping", b"nonce")
        self.assertEqual(decode_frame(encode_frame(message)), message)

    def test_database(self):
        db = ChainDatabase()
        db.put_utxo(b"x"*32, 0, 123, b"alice", 0, False)
        self.assertEqual(db.utxos(b"alice")[0][2], 123)
        db.spend(b"x"*32, 0)
        self.assertEqual(db.utxos(), [])

if __name__ == "__main__":
    unittest.main()

