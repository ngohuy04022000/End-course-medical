from __future__ import annotations

import argparse
from pathlib import Path

from .pipeline import run_pipeline


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build multimodal carotid dataset artifacts.")
    parser.add_argument(
        "--dataset-root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Folder containing the CSV file and CAROTID_IMAGES directory.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Where to write manifest.csv, splits.csv, and summary.json.",
    )
    parser.add_argument("--seed", type=int, default=42, help="Random seed for splits.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_dir = args.output_dir or (args.dataset_root / "outputs")
    summary = run_pipeline(args.dataset_root, output_dir, seed=args.seed)

    print("Dataset processed successfully.")
    print(f"Output folder: {output_dir}")
    print(f"Patients: {summary['total_patients']}")
    print(f"Plaque counts: {summary['plaque_present_counts']}")
    print(f"Risk categories: {summary['risk_category_counts']}")
    if summary["validation_issues"]:
        print(f"Validation issues: {len(summary['validation_issues'])}")
        for issue in summary["validation_issues"][:10]:
            print(f"- {issue}")
    else:
        print("Validation issues: none")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
