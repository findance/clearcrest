from dataclasses import dataclass
from enum import Enum
from clearcrest.consensus.params import CHANNEL_MAX_CAPACITY, CHANNEL_MIN_CAPACITY, DISPUTE_PHASE_BLOCKS, DISPUTE_PHASE_BOUNTIES

class ChannelStatus(str, Enum):
    OPEN = "open"
    DISPUTING = "disputing"
    CLOSED = "closed"

@dataclass
class Channel:
    channel_id: bytes
    alice_balance: int
    bob_balance: int
    state_number: int = 0
    anchored_state: int = 0
    status: ChannelStatus = ChannelStatus.OPEN
    close_height: int | None = None
    def __post_init__(self):
        capacity = self.alice_balance + self.bob_balance
        if not CHANNEL_MIN_CAPACITY <= capacity <= CHANNEL_MAX_CAPACITY: raise ValueError("channel capacity out of range")
    @property
    def capacity(self) -> int: return self.alice_balance + self.bob_balance
    def update(self, alice_balance: int, bob_balance: int) -> int:
        if self.status != ChannelStatus.OPEN or min(alice_balance, bob_balance) < 0 or alice_balance + bob_balance != self.capacity: raise ValueError("invalid channel update")
        self.alice_balance, self.bob_balance = alice_balance, bob_balance; self.state_number += 1
        return self.state_number
    def anchor(self, state_number: int) -> None:
        if self.status != ChannelStatus.OPEN or not self.anchored_state <= state_number <= self.state_number: raise ValueError("invalid anchor")
        self.anchored_state = state_number
    def cooperative_close(self) -> None:
        if self.status != ChannelStatus.OPEN: raise ValueError("channel not open")
        self.status = ChannelStatus.CLOSED
    def force_close(self, state_number: int, height: int) -> None:
        if self.status != ChannelStatus.OPEN or state_number < self.anchored_state or state_number > self.state_number: raise ValueError("stale or invalid force-close")
        self.status, self.close_height = ChannelStatus.DISPUTING, height
    def bounty_percent(self, height: int) -> int:
        if self.status != ChannelStatus.DISPUTING or self.close_height is None: return 0
        phase = (height - self.close_height) // DISPUTE_PHASE_BLOCKS
        return DISPUTE_PHASE_BOUNTIES[min(max(phase, 0), len(DISPUTE_PHASE_BOUNTIES) - 1)]
    def resolve(self, height: int, challenged: bool = False) -> int:
        if self.status != ChannelStatus.DISPUTING: raise ValueError("no dispute")
        if height < self.close_height + DISPUTE_PHASE_BLOCKS * len(DISPUTE_PHASE_BOUNTIES): raise ValueError("dispute window remains")
        bounty = self.capacity * self.bounty_percent(height) // 100 if challenged else 0
        self.status = ChannelStatus.CLOSED
        return bounty
