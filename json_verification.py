"""Phase 2 JSON verification script.

Run this file directly from VS Code (Run Python File). No CLI arguments are used.
Workflow:
1) Load File 1 (IP JSON) and File 2 (SI JSON)
2) Convert File 1 SSA values from IP to SI
3) Save both datasets as H5
4) Run NO_compare to generate Excel comparison output
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import NO_compare
import NO_conversion
import NO_file_tools
import pandas as pd
from json_parser import create_ssa_dataframe, read_json_to_dict


# =============================================================
# USER INPUTS (EDIT THESE TWO PATHS EACH PHASE)
# =============================================================
FILE1_IP_JSON_PATH = Path(r"C:\Users\msn\OneDrive\Never Gray\Software Development\OpenSES\verification\Phase 2 SI Verification\inferno_IP_P2.JSON")
FILE2_SI_JSON_PATH = Path(r"C:\Users\msn\OneDrive\Never Gray\Software Development\OpenSES\verification\Phase 2 SI Verification\inferno_SI_P2.JSON")

# File 1 converted H5 name rule requested by user:
# FILE1_IP_JSON_PATH stem + "_2_SI" + ".h5"
FILE1_CONVERTED_H5_PATH = FILE1_IP_JSON_PATH.with_name(
    f"{FILE1_IP_JSON_PATH.stem}_2_SI.h5"
)

# One-off correction for this JSON source: scale File 1 airflow prior to
# the standard IP->SI conversion step. Keep at 1.0 when not needed.
FILE1_AIRFLOW_PRECONVERSION_MULTIPLIER = 0.001

# File 2 H5 path (same stem, .h5 extension)
FILE2_SI_H5_PATH = FILE2_SI_JSON_PATH.with_suffix(".h5")
# =============================================================


def _load_ssa_from_json(json_path: Path, label: str) -> tuple[dict[str, Any], dict[str, Any]]:
    data_dictionary, diagnostics = read_json_to_dict(json_path)
    pit_count = diagnostics.get("pit_record_count", 0)
    df_ssa = create_ssa_dataframe(data_dictionary)

    print(f"[{label}] JSON: {json_path}")
    print(f"[{label}] pit_record_count: {pit_count}")
    print(f"[{label}] SSA shape: {df_ssa.shape}")

    if pit_count <= 0:
        raise ValueError(f"[{label}] No pit records found in {json_path}")
    if df_ssa.empty:
        raise ValueError(f"[{label}] SSA dataframe is empty for {json_path}")

    data = {"SSA": df_ssa}
    return data, diagnostics


def _normalize_ssa_for_compare(data: dict[str, Any], label: str) -> None:
    """Normalize SSA column dtypes so NO_compare arithmetic is stable.

    NO_compare removes object columns but keeps boolean columns. On newer numpy
    versions, subtracting booleans raises a TypeError, so booleans are cast to
    float values (0.0/1.0) before writing H5.
    """
    ssa = data.get("SSA")
    if not isinstance(ssa, pd.DataFrame):
        raise TypeError(f"[{label}] SSA table is missing or not a DataFrame")

    bool_columns = list(ssa.select_dtypes(include=["bool"]).columns)
    if bool_columns:
        for column in bool_columns:
            ssa[column] = ssa[column].astype(float)
        print(f"[{label}] Converted bool columns to float for compare: {bool_columns}")


def _apply_file1_airflow_multiplier(data: dict[str, Any], multiplier: float) -> None:
    """Apply one-off multiplier to File 1 airflow before unit conversion."""
    if multiplier == 1.0:
        return

    ssa = data.get("SSA")
    if not isinstance(ssa, pd.DataFrame):
        raise TypeError("[FILE1] SSA table is missing or not a DataFrame")
    if "Airflow" not in ssa.columns:
        raise KeyError("[FILE1] Airflow column not found in SSA")

    ssa["Airflow"] = pd.to_numeric(ssa["Airflow"], errors="coerce") * multiplier
    print(f"[FILE1] Applied one-off airflow multiplier: x{multiplier}")


def _save_h5_with_meta(
    data: dict[str, Any],
    h5_path: Path,
    ses_version: str,
    source_json_path: Path,
) -> Path:
    output_meta_data: dict[str, Any] = {
        "file_path": h5_path,
        "ses_version": ses_version,
        "source_file_type": "json",
        "source_file_path": str(source_json_path),
    }

    NO_file_tools.save_h5_file(data, output_meta_data)
    if not h5_path.exists():
        raise FileNotFoundError(f"Expected H5 file was not created: {h5_path}")

    # Read back to verify the artifact is valid and contains data.
    read_data, _ = NO_file_tools.read_h5_file(h5_path)
    ssa = read_data.get("SSA")
    if ssa is None or ssa.empty:
        raise ValueError(f"Saved H5 is missing non-empty SSA table: {h5_path}")

    print(f"[SAVE] H5 created: {h5_path}")
    print(f"[SAVE] H5 SSA shape: {ssa.shape}")
    return h5_path


def _build_compare_settings(file1_h5: Path, file2_h5: Path) -> dict[str, Any]:
    return {
        "ses_output_str": [str(file1_h5), str(file2_h5)],
        "visio_template": None,
        "simtime": -1,
        "output_conversion": "",
        "output": ["Compare"],
        "file_type": "H5_file",
        "path_exe": "",
    }


def _expected_compare_excel_path(file1_h5: Path, file2_h5: Path) -> Path:
    file_name = f"{file1_h5.stem}_to_{file2_h5.stem}"[:250] + ".xlsx"
    return file1_h5.parent / file_name


def main() -> None:
    print("=== Phase 2 JSON Verification ===")
    print(f"File 1 (IP JSON): {FILE1_IP_JSON_PATH}")
    print(f"File 2 (SI JSON): {FILE2_SI_JSON_PATH}")

    if not FILE1_IP_JSON_PATH.exists():
        raise FileNotFoundError(f"File 1 does not exist: {FILE1_IP_JSON_PATH}")
    if not FILE2_SI_JSON_PATH.exists():
        raise FileNotFoundError(f"File 2 does not exist: {FILE2_SI_JSON_PATH}")

    # 1) Load JSON to SSA
    file1_data, _ = _load_ssa_from_json(FILE1_IP_JSON_PATH, "FILE1")
    file2_data, _ = _load_ssa_from_json(FILE2_SI_JSON_PATH, "FILE2")
    _normalize_ssa_for_compare(file1_data, "FILE1")
    _normalize_ssa_for_compare(file2_data, "FILE2")
    _apply_file1_airflow_multiplier(file1_data, FILE1_AIRFLOW_PRECONVERSION_MULTIPLIER)

    # 2) Convert File 1 from IP -> SI
    file1_meta: dict[str, Any] = {
        "file_path": FILE1_CONVERTED_H5_PATH,
        "ses_version": "IP",
        "source_file_type": "json",
        "source_file_path": str(FILE1_IP_JSON_PATH),
    }
    file1_data, file1_meta = NO_conversion.convert_output_units(
        "IP_TO_SI",
        file1_data,
        file1_meta,
    )
    print(f"[FILE1] Conversion complete. ses_version: {file1_meta.get('ses_version')}")

    # 3) Save converted File 1 H5
    file1_h5 = _save_h5_with_meta(
        file1_data,
        FILE1_CONVERTED_H5_PATH,
        file1_meta.get("ses_version", "SI from IP"),
        FILE1_IP_JSON_PATH,
    )

    # 4) Save File 2 SI H5 (no conversion)
    file2_h5 = _save_h5_with_meta(
        file2_data,
        FILE2_SI_H5_PATH,
        "SI",
        FILE2_SI_JSON_PATH,
    )

    # 5) Compare and generate Excel report
    compare_settings = _build_compare_settings(file1_h5, file2_h5)
    NO_compare.compare_outputs(compare_settings)

    expected_excel = _expected_compare_excel_path(file1_h5, file2_h5)
    print("=== Run Summary ===")
    print(f"Converted H5 (File 1): {file1_h5}")
    print(f"Native SI H5 (File 2): {file2_h5}")
    print(f"Expected compare Excel: {expected_excel}")
    print(f"Excel exists: {expected_excel.exists()}")


if __name__ == "__main__":
    main()
