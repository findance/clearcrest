from dataclasses import dataclass
from clearcrest.crypto.hashing import sha3_256

@dataclass(frozen=True)
class HTLC:
    sender: bytes
    receiver: bytes
    amount: int
    payment_hash: bytes
    timeout_height: int
    claimed: bool = False
    def claim(self, preimage: bytes, height: int) -> "HTLC":
        if height >= self.timeout_height: raise ValueError("HTLC expired")
        if sha3_256(preimage) != self.payment_hash: raise ValueError("bad preimage")
        return HTLC(self.sender, self.receiver, self.amount, self.payment_hash, self.timeout_height, True)
    def refund(self, height: int) -> bytes:
        if self.claimed or height < self.timeout_height: raise ValueError("HTLC cannot be refunded")
        return self.sender

