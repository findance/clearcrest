import unittest
from clearcrest.channels.channel import Channel, ChannelStatus
from clearcrest.channels.htlc import HTLC
from clearcrest.consensus.params import INITIAL_REWARD, MAX_SUPPLY, RETARGET_INTERVAL, block_reward
from clearcrest.consensus.pow import adjust_target
from clearcrest.core.transaction import Transaction, TxInput, TxOutput, TxType, coinbase
from clearcrest.crypto.address import pubkey_to_address, validate_address
from clearcrest.crypto.hashing import sha3_256
from clearcrest.crypto.shamir import recover_secret, split_secret
from clearcrest.mempool.mempool import Mempool

class ProtocolTests(unittest.TestCase):
    def test_address_and_shamir(self):
        address = pubkey_to_address(b"public key")
        self.assertTrue(validate_address(address))
        self.assertFalse(validate_address(address[:-1] + "x"))
        shares = split_secret(b"recoverable secret", 5, 3)
        self.assertEqual(recover_secret([shares[0], shares[2], shares[4]]), b"recoverable secret")

    def test_canonical_transaction_and_rbf(self):
        inp = TxInput(b"a" * 32, 0)
        first = Transaction(TxType.TRANSFER, (inp,), (TxOutput(1000, b"recipient"),), rbf=True)
        replacement = Transaction(TxType.TRANSFER, (inp,), (TxOutput(900, b"recipient"),), rbf=True)
        pool = Mempool(); pool.add(first, 250); pool.add(replacement, 251)
        self.assertEqual(pool.ordered(), [replacement])
        with self.assertRaises(ValueError): TxOutput(MAX_SUPPLY + 1, b"x").serialize()
        self.assertEqual(coinbase(1, INITIAL_REWARD, b"miner").data, (1).to_bytes(8, "big"))

    def test_channels_and_htlc(self):
        channel = Channel(b"c" * 32, 10_000, 10_000)
        channel.update(9_000, 11_000); channel.anchor(1)
        with self.assertRaises(ValueError): channel.force_close(0, 10)
        channel.force_close(1, 10)
        self.assertEqual(channel.bounty_percent(155), 15)
        self.assertEqual(channel.resolve(442, challenged=True), 4_000)
        self.assertEqual(channel.status, ChannelStatus.CLOSED)
        preimage = b"secret"; htlc = HTLC(b"a", b"b", 10, sha3_256(preimage), 100)
        self.assertTrue(htlc.claim(preimage, 99).claimed)

    def test_supply_and_difficulty_window(self):
        self.assertEqual(block_reward(0), INITIAL_REWARD)
        self.assertLess(block_reward(210_000), INITIAL_REWARD)
        timestamps = [i * 600 for i in range(RETARGET_INTERVAL)]
        self.assertLess(adjust_target(10_000, timestamps), 10_000)

if __name__ == "__main__":
    unittest.main()

