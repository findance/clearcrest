from clearcrest.crypto.hashing import double_sha3

def merkle_root(txids: list[bytes]) -> bytes:
    if not txids: return b"\0" * 32
    if any(len(x) != 32 for x in txids): raise ValueError("txids must be 32 bytes")
    layer = txids[:]
    while len(layer) > 1:
        if len(layer) & 1: layer.append(layer[-1])
        layer = [double_sha3(layer[i] + layer[i + 1]) for i in range(0, len(layer), 2)]
    return layer[0]

