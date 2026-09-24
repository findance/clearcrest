"""Wallet state; signing requires a registered reviewed PQ provider."""
from dataclasses import dataclass, field
from clearcrest.crypto.address import pubkey_to_address
from clearcrest.crypto.keys import KeyRegistry, registry as default_registry
from clearcrest.crypto.shamir import split_secret
from clearcrest.core.transaction import Transaction, TxInput, TxOutput, TxType

@dataclass
class Wallet:
    private_key: bytes
    public_key: bytes
    key_version: int
    registry: KeyRegistry = field(default_factory=lambda: default_registry)
    utxos: dict[tuple[bytes, int], tuple[int, bytes]] = field(default_factory=dict)
    @classmethod
    def create(cls, version: int = 1, key_registry: KeyRegistry = default_registry) -> "Wallet":
        private_key, public_key = key_registry.generate_keypair(version)
        return cls(private_key, public_key, version, key_registry)
    @property
    def address(self) -> str: return pubkey_to_address(self.public_key, self.key_version)
    @property
    def balance(self) -> int: return sum(amount for amount, _ in self.utxos.values())
    def recovery_shares(self, n: int, k: int) -> list[bytes]: return split_secret(self.private_key, n, k)
    def build_payment(self, recipient: bytes, amount: int, fee: int, rbf: bool = False) -> Transaction:
        if amount <= 0 or fee < 0: raise ValueError("amount and fee must be valid")
        selected: list[tuple[tuple[bytes, int], tuple[int, bytes]]] = []; total = 0
        for point, entry in self.utxos.items():
            selected.append((point, entry)); total += entry[0]
            if total >= amount + fee: break
        if total < amount + fee: raise ValueError("insufficient wallet balance")
        inputs = tuple(TxInput(txid, index, public_key=self.public_key) for (txid, index), _ in selected)
        outputs = [TxOutput(amount, recipient)]
        if change := total - amount - fee: outputs.append(TxOutput(change, self.address.encode()))
        unsigned = Transaction(TxType.TRANSFER, inputs, tuple(outputs), rbf=rbf)
        provider = self.registry.provider(self.key_version)
        signed_inputs = tuple(TxInput(item.prev_txid, item.output_index, provider.sign(self.private_key, unsigned.txid), self.public_key) for item in inputs)
        return Transaction(TxType.TRANSFER, signed_inputs, tuple(outputs), rbf=rbf)
