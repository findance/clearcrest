# ClearCrest

ClearCrest is an experimental, dependency-light cryptocurrency protocol reference.
It implements deterministic wire objects, SHA3-256 hashing, Bech32m addresses,
fixed-point supply rules, block headers and merkle commitments, a compact membership
filter, SQLite UTXO persistence, RBF mempool policy, native channel/HTLC state,
watchtower stale-close detection, authenticated P2P framing, compact block relay,
wallet coin selection, and Shamir recovery.

## Security status

This is **not production software** and must not secure real funds. In particular,
the signing interface is deliberately an adapter boundary: a vetted FIPS 204 ML-DSA
implementation must be supplied before a network launch. Hashes and address encodings
do not make a scheme quantum-safe by themselves.

The local keystore, live networking, peer discovery, stealth-address KEM, full chain
reorganization, and consensus signatures are intentionally not represented as finished
features. They need a separately reviewed design and deployment implementation; exposing
stub implementations for them would be dangerous.

## Quick start

```bash
python -m unittest discover -s tests -v
python -m clearcrest.cli.main info
```

The project uses only the Python standard library, which keeps the reference easy to
audit and avoids native dependency costs. Add a reviewed signature-provider package
only at the deployment boundary.
