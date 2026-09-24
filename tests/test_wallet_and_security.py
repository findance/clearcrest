import unittest
from clearcrest.channels.channel import Channel
from clearcrest.channels.watchtower import Watchtower
from clearcrest.crypto.keys import KeyRegistry
from clearcrest.wallet.wallet import Wallet

class FakeProvider:
    version = 1
    def generate_keypair(self): return b"private", b"public"
    def sign(self, private_key, message): return b"sig:" + message
    def verify(self, public_key, message, signature): return signature == b"sig:" + message

class WalletAndSecurityTests(unittest.TestCase):
    def test_missing_provider_fails_closed(self):
        with self.assertRaises(RuntimeError): Wallet.create()

    def test_wallet_uses_provider_and_watchtower_detects_stale_close(self):
        registry = KeyRegistry({}); registry.register(FakeProvider())
        wallet = Wallet.create(key_registry=registry)
        wallet.utxos[(b"a"*32, 0)] = (1_000, b"mine")
        tx = wallet.build_payment(b"recipient", 500, 250, rbf=True)
        self.assertTrue(tx.inputs[0].signature.startswith(b"sig:"))
        channel = Channel(b"c"*32, 10_000, 10_000)
        channel.update(9_000, 11_000); channel.force_close(1, 50)
        tower = Watchtower(); tower.register_watch(channel, 2, b"proof")
        self.assertEqual(tower.scan_force_close(channel.channel_id, 1), b"proof")

if __name__ == "__main__":
    unittest.main()

