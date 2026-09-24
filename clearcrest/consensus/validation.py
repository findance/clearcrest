from clearcrest.consensus.params import MAX_SUPPLY, MIN_FEE
from clearcrest.core.transaction import Transaction, TxType

def validate_transaction(tx: Transaction, available: dict[tuple[bytes, int], int], fee: int) -> None:
    if any(not 0 <= output.amount <= MAX_SUPPLY for output in tx.outputs): raise ValueError("amount out of range")
    if tx.tx_type == TxType.COINBASE:
        if tx.inputs or len(tx.data) != 8: raise ValueError("malformed coinbase")
        return
    if not tx.inputs or not tx.outputs: raise ValueError("transaction needs inputs and outputs")
    points = tx.spent_outpoints()
    if len(points) != len(tx.inputs) or any(point not in available for point in points): raise ValueError("missing or duplicate UTXO")
    input_total = sum(available[point] for point in points)
    if tx.output_total() + fee > input_total: raise ValueError("insufficient input")
    if fee < MIN_FEE: raise ValueError("fee below minimum")

