"""Opt-in watchtower registry for detecting stale force-close states."""
from dataclasses import dataclass
from .channel import Channel, ChannelStatus

@dataclass
class Watch:
    channel: Channel
    latest_state: int
    revocation_proof: bytes

class Watchtower:
    def __init__(self): self._watches: dict[bytes, Watch] = {}
    def register_watch(self, channel: Channel, latest_state: int, revocation_proof: bytes) -> None:
        if latest_state < channel.anchored_state: raise ValueError("watch state predates anchor")
        self._watches[channel.channel_id] = Watch(channel, latest_state, revocation_proof)
    def scan_force_close(self, channel_id: bytes, state_number: int) -> bytes | None:
        watch = self._watches.get(channel_id)
        if not watch or watch.channel.status != ChannelStatus.DISPUTING: return None
        return watch.revocation_proof if state_number < watch.latest_state else None

