from __future__ import annotations

import csv
import json
import random
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class PatientRecord:
    patient_id: str
    age: int
    sex: str
    lpa_mg_dl: float
    apob_mg_dl: float
    ldl_c_mg_dl: float
    triglyceride_mg_dl: float
    total_cholesterol_mg_dl: float
    non_hdl_mg_dl: float
    imt_mm: float
    plaque_present: int
    plaque_echogenicity: str
    baseline_risk_score: float
    baseline_risk_category: str
    associated_images: list[str]


def _parse_images(raw_value: str) -> list[str]:
    if not raw_value:
        return []
    return [item.strip() for item in raw_value.split(",") if item.strip()]


def load_records(csv_path: Path) -> list[PatientRecord]:
    records: list[PatientRecord] = []
    with csv_path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            records.append(
                PatientRecord(
                    patient_id=row["Patient_ID"],
                    age=int(float(row["Age"])),
                    sex=row["Sex"],
                    lpa_mg_dl=float(row["Lp(a)_mg_dL"]),
                    apob_mg_dl=float(row["ApoB_mg_dL"]),
                    ldl_c_mg_dl=float(row["LDL_C_mg_dL"]),
                    triglyceride_mg_dl=float(row["Triglyceride_mg_dL"]),
                    total_cholesterol_mg_dl=float(row["Total_Cholesterol_mg_dL"]),
                    non_hdl_mg_dl=float(row["Non_HDL_mg_dL"]),
                    imt_mm=float(row["IMT_mm"]),
                    plaque_present=int(row["Plaque_present"]),
                    plaque_echogenicity=row["Plaque_echogenicity"],
                    baseline_risk_score=float(row["Baseline_Risk_Score"]),
                    baseline_risk_category=row["Baseline_Risk_Category"],
                    associated_images=_parse_images(row["Associated_Images"]),
                )
            )
    return records


def validate_records(records: Iterable[PatientRecord], image_dir: Path) -> list[str]:
    issues: list[str] = []
    for record in records:
        if not record.associated_images:
            issues.append(f"{record.patient_id}: missing Associated_Images")
            continue
        for image_name in record.associated_images:
            image_path = image_dir / image_name
            if not image_path.exists():
                issues.append(f"{record.patient_id}: missing image {image_name}")
    return issues


def build_manifest(records: Iterable[PatientRecord], image_dir: Path) -> list[dict[str, object]]:
    manifest: list[dict[str, object]] = []
    for record in records:
        image_paths = [str((image_dir / image_name).resolve()) for image_name in record.associated_images]
        manifest.append(
            {
                "patient_id": record.patient_id,
                "age": record.age,
                "sex": record.sex,
                "plaque_present": record.plaque_present,
                "plaque_echogenicity": record.plaque_echogenicity,
                "baseline_risk_score": record.baseline_risk_score,
                "baseline_risk_category": record.baseline_risk_category,
                "imt_mm": record.imt_mm,
                "image_count": len(image_paths),
                "image_group": "multi_image" if len(image_paths) > 1 else "imt_only",
                "images": "|".join(image_paths),
            }
        )
    return manifest


def _split_group(items: list[PatientRecord], seed: int) -> dict[str, list[PatientRecord]]:
    rng = random.Random(seed)
    shuffled = list(items)
    rng.shuffle(shuffled)

    total = len(shuffled)
    train_count = round(total * 0.7)
    val_count = round(total * 0.15)
    test_count = total - train_count - val_count

    if test_count < 0:
        test_count = 0
        val_count = max(0, total - train_count)

    train_end = train_count
    val_end = train_end + val_count
    return {
        "train": shuffled[:train_end],
        "val": shuffled[train_end:val_end],
        "test": shuffled[val_end:],
    }


def build_splits(records: Iterable[PatientRecord], seed: int = 42) -> dict[str, list[str]]:
    records_by_label: dict[int, list[PatientRecord]] = defaultdict(list)
    for record in records:
        records_by_label[record.plaque_present].append(record)

    split_assignments: dict[str, list[str]] = {"train": [], "val": [], "test": []}
    for label, group_records in records_by_label.items():
        group_splits = _split_group(group_records, seed + label)
        for split_name, split_records in group_splits.items():
            split_assignments[split_name].extend(record.patient_id for record in split_records)

    for split_name in split_assignments:
        split_assignments[split_name].sort()
    return split_assignments


def summarize(records: Iterable[PatientRecord]) -> dict[str, object]:
    records_list = list(records)
    plaque_counts = Counter(record.plaque_present for record in records_list)
    echogenicity_counts = Counter(record.plaque_echogenicity for record in records_list)
    risk_counts = Counter(record.baseline_risk_category for record in records_list)
    image_counts = Counter(len(record.associated_images) for record in records_list)

    return {
        "total_patients": len(records_list),
        "plaque_present_counts": {str(key): value for key, value in sorted(plaque_counts.items())},
        "echogenicity_counts": dict(sorted(echogenicity_counts.items())),
        "risk_category_counts": dict(sorted(risk_counts.items())),
        "image_count_distribution": {str(key): value for key, value in sorted(image_counts.items())},
    }


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def run_pipeline(dataset_root: Path, output_dir: Path, seed: int = 42) -> dict[str, object]:
    csv_path = dataset_root / "carotid_clinical_dataset_300cases.csv"
    image_dir = dataset_root / "CAROTID_IMAGES"

    records = load_records(csv_path)
    issues = validate_records(records, image_dir)
    manifest = build_manifest(records, image_dir)
    splits = build_splits(records, seed=seed)
    summary = summarize(records)
    summary["validation_issues"] = issues
    summary["split_counts"] = {name: len(patient_ids) for name, patient_ids in splits.items()}

    output_dir.mkdir(parents=True, exist_ok=True)
    write_csv(
        output_dir / "manifest.csv",
        manifest,
        [
            "patient_id",
            "age",
            "sex",
            "plaque_present",
            "plaque_echogenicity",
            "baseline_risk_score",
            "baseline_risk_category",
            "imt_mm",
            "image_count",
            "image_group",
            "images",
        ],
    )
    write_csv(
        output_dir / "splits.csv",
        [
            {"patient_id": patient_id, "split": split_name}
            for split_name, patient_ids in splits.items()
            for patient_id in patient_ids
        ],
        ["patient_id", "split"],
    )
    (output_dir / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    return summary
