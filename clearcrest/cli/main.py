"""Local, non-networked operational CLI."""
import argparse
import json
from clearcrest.consensus.params import MAX_SUPPLY, MIN_FEE, QUANTA_PER_CCR

def _info(_: argparse.Namespace) -> int:
    print(json.dumps({"network_port": 9333, "max_supply_quanta": MAX_SUPPLY, "minimum_fee_quanta": MIN_FEE, "quanta_per_ccr": QUANTA_PER_CCR}, sort_keys=True))
    return 0

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="clearcrest")
    subcommands = parser.add_subparsers(required=True)
    info = subcommands.add_parser("info", help="show immutable network parameters")
    info.set_defaults(handler=_info)
    args = parser.parse_args(argv)
    return args.handler(args)

if __name__ == "__main__":
    raise SystemExit(main())

