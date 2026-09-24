# ClearCrest

ClearCrest is an experimental, dependency-light cryptocurrency protocol reference.
It implements deterministic wire objects, SHA3-256 hashing, Bech32m addresses,
fixed-point supply rules, RBF mempool policy, a native channel state machine, HTLCs,
and Shamir recovery.

## Security status

This is **not production software** and must not secure real funds. In particular,
the signing interface is deliberately an adapter boundary: a vetted FIPS 204 ML-DSA
implementation must be supplied before a network launch. Hashes and address encodings
do not make a scheme quantum-safe by themselves.

## Quick start

```bash
python -m unittest discover -s tests -v
```

The project uses only the Python standard library, which keeps the reference easy to
audit and avoids native dependency costs. Add a reviewed signature-provider package
only at the deployment boundary.

