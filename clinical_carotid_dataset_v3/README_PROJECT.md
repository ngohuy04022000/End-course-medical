# Carotid Multimodal Dataset Project

This folder now contains a small, runnable Python project for the carotid artery atherosclerosis dataset.

## What it does

- Reads `carotid_clinical_dataset_300cases.csv`
- Verifies that referenced images exist in `CAROTID_IMAGES/`
- Builds `outputs/manifest.csv` with one row per patient
- Builds `outputs/splits.csv` with a deterministic train/val/test split
- Writes `outputs/summary.json` with dataset counts and validation issues

## How to run

```powershell
Set-Location "d:\Tai Lieu Hoc Tap Cao Hoc\Xu ly tin hieu va hinh anh y khoa\End-Course\clinical_carotid_dataset_v3"
"d:/Tai Lieu Hoc Tap Cao Hoc/Xu ly tin hieu va hinh anh y khoa/End-Course/.venv/Scripts/python.exe" -m carotid_multimodal
```

You can also change the output folder:

```powershell
"d:/Tai Lieu Hoc Tap Cao Hoc/Xu ly tin hieu va hinh anh y khoa/End-Course/.venv/Scripts/python.exe" -m carotid_multimodal --output-dir outputs_v2
```

## Notes

- The implementation follows the CSV and image layout that is actually present in the workspace.
- The original RTF description mentions a different CSV filename and different class counts; the pipeline uses the real file and reports the real distributions.
