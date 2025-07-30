# etsi/watchdog/cli.py

import argparse
import pandas as pd
from . import DriftCheck


def run_cli():
    parser = argparse.ArgumentParser(description="ETSI Drift Watchdog CLI")
    parser.add_argument("--ref", required=True, help="Path to reference CSV file")
    parser.add_argument("--live", required=True, help="Path to live CSV file")
    parser.add_argument("--features", nargs="+", help="List of features to check")
    parser.add_argument("--algo", default="psi", help="Drift algorithm (default: psi)")
    parser.add_argument("--threshold", type=float, default=0.2, help="Drift threshold (default: 0.2)")
    parser.add_argument("--out", help="Output JSON file")

    args = parser.parse_args()

    ref_df = pd.read_csv(args.ref)
    live_df = pd.read_csv(args.live)

    checker = DriftCheck(ref_df, algorithm=args.algo, threshold=args.threshold)
    results = checker.run(live_df, features=args.features or list(ref_df.columns))

    for feat, res in results.items():
        print(f"\n{feat} ➤ {res.summary()}")
        if args.out:
            res.to_json(f"{args.out}_{feat}.json")


if __name__ == "__main__":
    run_cli()
