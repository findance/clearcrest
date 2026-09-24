"""Length-delimited P2P framing with strict size and command validation."""
from dataclasses import dataclass
from clearcrest.crypto.hashing import double_sha3

MAGIC = b"\xcc" * 4
MAX_MESSAGE_SIZE = 6 * 1024 * 1024
COMMANDS = frozenset({"version", "verack", "inv", "getdata", "block", "tx", "getblocks", "ping", "pong", "channel_alert", "cmpctblock", "getblocktxn", "blocktxn", "getcfilters", "cfilter"})

@dataclass(frozen=True)
class Message:
    command: str
    payload: bytes = b""

def encode_frame(message: Message) -> bytes:
    if message.command not in COMMANDS or len(message.payload) > MAX_MESSAGE_SIZE: raise ValueError("invalid network message")
    command = message.command.encode("ascii")
    return MAGIC + command.ljust(12, b"\0") + len(message.payload).to_bytes(4, "big") + double_sha3(message.payload)[:4] + message.payload

def decode_frame(frame: bytes) -> Message:
    if len(frame) < 24 or frame[:4] != MAGIC: raise ValueError("bad message magic")
    command = frame[4:16].rstrip(b"\0").decode("ascii")
    size = int.from_bytes(frame[16:20], "big")
    if command not in COMMANDS or size > MAX_MESSAGE_SIZE or len(frame) != 24 + size: raise ValueError("invalid frame")
    payload = frame[24:]
    if double_sha3(payload)[:4] != frame[20:24]: raise ValueError("bad payload checksum")
    return Message(command, payload)

