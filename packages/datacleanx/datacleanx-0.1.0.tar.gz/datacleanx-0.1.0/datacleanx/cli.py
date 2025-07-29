# datacleanx/cli.py

import argparse
import pandas as pd
import json
import os
from datetime import datetime
from datacleanx.cleaner import Cleaner
from datacleanx.report import DataCleanerReport  # Optional if you're using custom report handling

def main():
    parser = argparse.ArgumentParser(description="🧼 Clean your CSV files with datacleanx")
    parser.add_argument("input", help="Path to input CSV file")
    parser.add_argument("--impute", choices=["mean", "median", "mode"], default="mean", help="Imputation strategy")
    parser.add_argument("--encode", choices=["label", "onehot"], help="Encoding strategy for categoricals")
    parser.add_argument("--remove-outliers", action="store_true", help="Remove outliers")
    parser.add_argument("--scale", choices=["standard", "minmax", "robust"], help="Scale numeric features")
    parser.add_argument("--output-name", help="Optional base name for output file (no extension)")
    parser.add_argument("--report", help="Optional path to save cleaning report as JSON")

    args = parser.parse_args()

    # Load data
    df = pd.read_csv(args.input)

    # Initialize cleaner
    cleaner = Cleaner(
        impute_strategy=args.impute,
        encode_categoricals=args.encode,
        remove_outliers=args.remove_outliers,
        scale_numerics=args.scale
    )

    # Clean data
    cleaned = cleaner.clean(df)

    # Ensure outputs directory exists
    os.makedirs("outputs", exist_ok=True)

    # Timestamp for filenames
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Build suffix for filename
    suffix_parts = []
    if args.impute:
        suffix_parts.append("impute")
    if args.encode:
        suffix_parts.append("encode")
    if args.remove_outliers:
        suffix_parts.append("outliers")
    if args.scale:
        suffix_parts.append("scale")
    suffix = "_".join(suffix_parts) or "cleaned"

    # Build output filename
    if args.output_name:
        output_path = f"outputs/{args.output_name}_{timestamp}.csv"
        report_filename = f"outputs/{args.output_name}_report_{timestamp}.json"
    else:
        output_path = f"outputs/{suffix}_{timestamp}.csv"
        report_filename = f"outputs/{suffix}_report_{timestamp}.json"

    # Save cleaned data
    cleaned.to_csv(output_path, index=False)
    print("✅ Data cleaned and saved to", output_path)

    # Generate and print report
    report = cleaner.report()
    print("📝 Report:", report)

    # Save report
    if args.report:
        with open(args.report, "w") as f:
            json.dump(report, f, indent=4)
        print(f"🧾 Report saved to {args.report}")
    else:
        with open(report_filename, "w") as f:
            json.dump(report, f, indent=4)
        print(f"🧾 Report auto-saved to {report_filename}")
