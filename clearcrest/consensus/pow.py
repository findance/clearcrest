from statistics import median
from clearcrest.crypto.hashing import double_sha3
from .params import MAX_TARGET, RETARGET_INTERVAL, TARGET_BLOCK_SECONDS

def valid_pow(header: bytes, target: int) -> bool:
    return 0 < target <= MAX_TARGET and int.from_bytes(double_sha3(header), "big") <= target

def adjust_target(previous_target: int, timestamps: list[int]) -> int:
    """Retarget only from an exact 2016-header window; avoids off-by-one windows."""
    if len(timestamps) != RETARGET_INTERVAL: raise ValueError("need exactly retarget interval timestamps")
    if any(b < a for a, b in zip(timestamps, timestamps[1:])): raise ValueError("timestamps must be monotonic")
    actual = timestamps[-1] - timestamps[0]
    expected = TARGET_BLOCK_SECONDS * RETARGET_INTERVAL
    actual = max(expected // 4, min(actual, expected * 4))
    return min(MAX_TARGET, max(1, previous_target * actual // expected))

def median_time_past(timestamps: list[int]) -> int:
    if not timestamps: raise ValueError("timestamps required")
    return int(median(timestamps[-11:]))

