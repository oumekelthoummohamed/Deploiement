import argparse
from pathlib import Path

import pandas as pd
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset

FEATURE_COLS = [
    "CreditScore",
    "Age",
    "Tenure",
    "Balance",
    "NumOfProducts",
    "HasCrCard",
    "IsActiveMember",
    "EstimatedSalary",
    "Geography_Germany",
    "Geography_Spain",
]


def load_features(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    return df[FEATURE_COLS]


def simulate_drift(ref: pd.DataFrame) -> pd.DataFrame:
    cur = ref.sample(n=min(1000, len(ref)), random_state=42).copy()
    cur["Age"] = (cur["Age"] + 5).clip(lower=18, upper=100)
    cur["Balance"] = (cur["Balance"] * 1.2).clip(lower=0)
    cur["EstimatedSalary"] = (cur["EstimatedSalary"] * 0.9).clip(lower=0)
    cur["CreditScore"] = (cur["CreditScore"] - 20).clip(lower=300, upper=850)
    return cur


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate data drift report")
    parser.add_argument("--reference", default="Data/bank_churn.csv")
    parser.add_argument("--current", default="")
    parser.add_argument("--out", default="reports/drift_report.html")
    args = parser.parse_args()

    ref = load_features(args.reference)

    if args.current:
        cur = load_features(args.current)
    else:
        cur = simulate_drift(ref)

    report = Report(metrics=[DataDriftPreset()])
    report.run(reference_data=ref, current_data=cur)

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    report.save_html(str(out_path))

    print(f"Drift report saved to {out_path}")


if __name__ == "__main__":
    main()
