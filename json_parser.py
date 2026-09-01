"""Standalone SES JSON loader.

Scope for this module:
- Read SES JSON into native Python objects (dict/list).
- Provide lightweight diagnostics and warnings.
- Build SSA dataframe from JSON segment/section data.
- Create H5 from JSON and optionally convert H5 outputs from IP to SI.

Out of scope for this module:
- Integration with NO_run pipeline.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import pandas as pd
import NO_conversion
import NO_Excel_R01
import NO_file_tools

OPTIONAL_PIT_KEYS = [
    "Train_Data",
    "Section_Data",
    "Segment_Data",
    "Subsegment_Data",
]

OPTIONAL_SECTION_KEYS = [
    "Section",
    "Segment",
    "Airflow",
    "Pressure_Change",
    "Buoyancy",
]

OPTIONAL_SEGMENT_KEYS = [
    "Segment",
    "Air_Velocity",
    "Line",
    "Reynolds_Number",
    "Number_Of_Trains",
]

OPTIONAL_SUBSEGMENT_KEYS = [
    "Subsegment_ID",
    "Air_Temp",
    "Humidity",
    "Sensible",
    "Latent",
    "Wall_Temp",
]


class JsonParserError(Exception):
    """Raised when the JSON file cannot be loaded."""


def _type_name(value: Any) -> str:
    return type(value).__name__


def _collect_pit_warnings(record: dict[str, Any], index: int) -> list[str]:
    warnings: list[str] = []

    for key in OPTIONAL_PIT_KEYS:
        if key not in record:
            warnings.append(f"pit[{index}] missing optional key: {key}")

    section_rows = record.get("Section_Data")
    if isinstance(section_rows, list) and section_rows:
        first_row = section_rows[0]
        if isinstance(first_row, dict):
            for key in OPTIONAL_SECTION_KEYS:
                if key not in first_row:
                    warnings.append(
                        f"pit[{index}].Section_Data[0] missing optional key: {key}"
                    )

    segment_rows = record.get("Segment_Data")
    if isinstance(segment_rows, list) and segment_rows:
        first_row = segment_rows[0]
        if isinstance(first_row, dict):
            for key in OPTIONAL_SEGMENT_KEYS:
                if key not in first_row:
                    warnings.append(
                        f"pit[{index}].Segment_Data[0] missing optional key: {key}"
                    )

    subsegment_rows = record.get("Subsegment_Data")
    if isinstance(subsegment_rows, list) and subsegment_rows:
        first_row = subsegment_rows[0]
        if isinstance(first_row, dict):
            for key in OPTIONAL_SUBSEGMENT_KEYS:
                if key not in first_row:
                    warnings.append(
                        f"pit[{index}].Subsegment_Data[0] missing optional key: {key}"
                    )

    return warnings


def inspect_json_structure(data: Any) -> dict[str, Any]:
    """Inspect JSON shape and return non-fatal diagnostics."""
    diagnostics: dict[str, Any] = {
        "top_level_type": _type_name(data),
        "record_count": 0,
        "info_present": False,
        "pit_record_count": 0,
        "top_level_keys": [],
        "sample_pit_keys": [],
        "warnings": [],
    }

    warnings: list[str] = []

    if isinstance(data, list):
        diagnostics["record_count"] = len(data)

        if data and isinstance(data[0], dict):
            diagnostics["top_level_keys"] = sorted(list(data[0].keys()))
            diagnostics["info_present"] = "info" in data[0]

        for index, record in enumerate(data):
            if not isinstance(record, dict):
                warnings.append(f"record[{index}] is {_type_name(record)}, expected dict")
                continue

            if "Pit" in record:
                diagnostics["pit_record_count"] += 1
                if not diagnostics["sample_pit_keys"]:
                    diagnostics["sample_pit_keys"] = sorted(list(record.keys()))
                warnings.extend(_collect_pit_warnings(record, index))

        if diagnostics["pit_record_count"] == 0:
            warnings.append("no pit-like records found (missing 'Pit' keys)")

    elif isinstance(data, dict):
        diagnostics["record_count"] = len(data)
        diagnostics["top_level_keys"] = sorted(list(data.keys()))
        diagnostics["info_present"] = "info" in data

        if "Pit" in data:
            diagnostics["pit_record_count"] = 1
            diagnostics["sample_pit_keys"] = sorted(list(data.keys()))
            warnings.extend(_collect_pit_warnings(data, 0))
        else:
            warnings.append("top-level object has no 'Pit' key")

    else:
        warnings.append(
            "top-level JSON should usually be list or dict for SES payloads"
        )

    diagnostics["warnings"] = warnings
    diagnostics["warning_count"] = len(warnings)
    return diagnostics


def read_json_to_dict(json_path: str | Path) -> tuple[Any, dict[str, Any]]:
    """Read JSON and return (data, diagnostics).

    The returned `data` is exactly what `json.load` produces.
    """
    path = Path(json_path)

    if not path.exists():
        raise JsonParserError(f"File not found: {path}")

    try:
        with open(path, "r", encoding="utf-8") as file_obj:
            data = json.load(file_obj)
    except json.JSONDecodeError as exc:
        raise JsonParserError(f"Invalid JSON in {path}: {exc}") from exc
    except OSError as exc:
        raise JsonParserError(f"Unable to read {path}: {exc}") from exc

    diagnostics = inspect_json_structure(data)
    diagnostics["file_path"] = str(path)
    return data, diagnostics


def _segment_from_row(row: dict[str, Any]) -> Any:
    if "Segment" in row:
        return row.get("Segment")
    return row.get("Section")


def _format_time_for_id(time_value: Any) -> str:
    try:
        return str(float(time_value))
    except (TypeError, ValueError):
        return str(time_value)


def _format_segment_for_id(segment_value: Any) -> str:
    try:
        as_float = float(segment_value)
        if as_float.is_integer():
            return str(int(as_float))
        return str(as_float)
    except (TypeError, ValueError):
        return str(segment_value)


def _safe_float(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _parse_subsegment_id(subsegment_id: Any) -> tuple[Any, Any, Any]:
    """Return (section, segment, sub) parsed from values like '1 -  3 - 10'."""
    if not isinstance(subsegment_id, str):
        return None, None, None

    parts = [part.strip() for part in subsegment_id.split("-")]
    if len(parts) < 3:
        return None, None, None

    values: list[Any] = []
    for part in parts[:3]:
        try:
            values.append(int(float(part)))
        except (TypeError, ValueError):
            values.append(part)
    return values[0], values[1], values[2]


def _iter_pit_records(data_dictionary: Any):
    if isinstance(data_dictionary, list):
        for record in data_dictionary:
            if isinstance(record, dict) and "Pit" in record:
                yield record
    elif isinstance(data_dictionary, dict) and "Pit" in data_dictionary:
        yield data_dictionary


def create_ssa_dataframe(data_dictionary: Any) -> pd.DataFrame:
    """Create an SSA dataframe from SES JSON dictionary data.

    Required first columns are: time, Segment, ID, Title, Airflow, Air_Velocity.
    Additional JSON fields are appended afterward.
    """
    rows: list[dict[str, Any]] = []
    additional_columns: list[str] = []
    seen_additional: set[str] = set()

    reserved = {"time", "Segment", "ID", "Title", "Airflow", "Air_Velocity", "Section"}

    for pit_record in _iter_pit_records(data_dictionary):
        time_value = pit_record.get("Pit")
        section_data = pit_record.get("Section_Data")
        segment_data = pit_record.get("Segment_Data")
        section_rows = section_data if isinstance(section_data, list) else []
        segment_rows = segment_data if isinstance(segment_data, list) else []

        section_by_segment: dict[Any, dict[str, Any]] = {}
        for section_row in section_rows:
            if isinstance(section_row, dict):
                segment_key = _segment_from_row(section_row)
                section_by_segment[segment_key] = section_row

        segment_by_segment: dict[Any, dict[str, Any]] = {}
        for segment_row in segment_rows:
            if isinstance(segment_row, dict):
                segment_key = _segment_from_row(segment_row)
                segment_by_segment[segment_key] = segment_row

        all_segments = list({*section_by_segment.keys(), *segment_by_segment.keys()})
        all_segments.sort(key=lambda value: (value is None, value))

        for segment_value in all_segments:
            section_row = section_by_segment.get(segment_value, {})
            segment_row = segment_by_segment.get(segment_value, {})
            id_time = _format_time_for_id(time_value)
            id_segment = _format_segment_for_id(segment_value)

            row: dict[str, Any] = {
                "time": time_value,
                "Segment": segment_value,
                "ID": f"{id_time}_{id_segment}",
                "Title": "",
                "Airflow": section_row.get("Airflow"),
                "Air_Velocity": segment_row.get("Air_Velocity"),
            }

            for source_row in (section_row, segment_row):
                for key, value in source_row.items():
                    if key in reserved:
                        continue
                    if key not in row:
                        row[key] = value
                    else:
                        # Keep the first source value if duplicate keys appear.
                        row[key] = row[key] if row[key] is not None else value
                    if key not in seen_additional:
                        seen_additional.add(key)
                        additional_columns.append(key)

            rows.append(row)

    first_columns = ["time", "Segment", "ID", "Title", "Airflow", "Air_Velocity"]
    ordered_columns = first_columns + [col for col in additional_columns if col not in first_columns]
    return pd.DataFrame(rows, columns=ordered_columns)


def create_sst_dataframe(data_dictionary: Any) -> pd.DataFrame:
    """Create an SST dataframe from SES JSON dictionary data.

    Uses Subsegment_Data rows and keeps compatibility with parser-style columns
    while allowing additional Phase 3 fields to flow through automatically.
    """
    rows: list[dict[str, Any]] = []
    additional_columns: list[str] = []
    seen_additional: set[str] = set()

    for pit_record in _iter_pit_records(data_dictionary):
        time_value = pit_record.get("Pit")
        subsegment_data = pit_record.get("Subsegment_Data")
        subsegment_rows = subsegment_data if isinstance(subsegment_data, list) else []

        for subsegment_row in subsegment_rows:
            if not isinstance(subsegment_row, dict):
                continue

            _, segment_value, sub_value = _parse_subsegment_id(
                subsegment_row.get("Subsegment_ID")
            )
            if segment_value is None or sub_value is None:
                continue

            row: dict[str, Any] = {
                "Time": _safe_float(time_value),
                "Segment": segment_value,
                "Sub": sub_value,
                "Air_Temp": subsegment_row.get("Air_Temp"),
                "Humidity": subsegment_row.get("Humidity"),
                "Sensible": subsegment_row.get("Sensible"),
                "Latent": subsegment_row.get("Latent"),
                "Wall_Temp": subsegment_row.get("Wall_Temp"),
                # Keep convection mapping strict until field semantics are verified.
                "Convection_to_Wall": subsegment_row.get("Convection_to_Wall"),
                # Empirical match against NO_parser output indicates Qradss is
                # radiation in Btu/s, while SST Radiation_to_Wall uses Btu/h.
                "Radiation_to_Wall": subsegment_row.get("Radiation_to_Wall", (
                    (_safe_float(subsegment_row.get("Qradss")) * 3600)
                    if _safe_float(subsegment_row.get("Qradss")) is not None
                    else None
                )),
            }

            reserved = {
                "Subsegment_ID",
                "Air_Temp",
                "Humidity",
                "Sensible",
                "Latent",
                "Wall_Temp",
                "Convection_to_Wall",
                "Radiation_to_Wall",
            }
            for key, value in subsegment_row.items():
                if key in reserved:
                    continue
                row[key] = value
                if key not in seen_additional:
                    seen_additional.add(key)
                    additional_columns.append(key)

            rows.append(row)

    df_sst = pd.DataFrame(rows)
    if df_sst.empty:
        return df_sst

    for column in ["Time", "Segment", "Sub"]:
        df_sst[column] = pd.to_numeric(df_sst[column], errors="coerce")
    df_sst["Segment"] = pd.to_numeric(df_sst["Segment"], downcast="integer")
    df_sst["Sub"] = pd.to_numeric(df_sst["Sub"], downcast="integer")

    df_sst = df_sst.set_index(["Time", "Segment", "Sub"]).sort_index()
    df_sst["ID"] = (
        df_sst.index.get_level_values(0).astype(str)
        + "_"
        + df_sst.index.get_level_values(1).astype(str)
        + "_"
        + df_sst.index.get_level_values(2).astype(str)
    )

    sst_first_columns = [
        "ID",
        "Air_Temp",
        "Humidity",
        "Sensible",
        "Latent",
        "Wall_Temp",
        "Convection_to_Wall",
        "Radiation_to_Wall",
    ]
    preferred_existing = [col for col in sst_first_columns if col in df_sst.columns]

    remaining_columns: list[str] = []
    seen_remaining: set[str] = set()
    for col in df_sst.columns.tolist() + additional_columns:
        if col in preferred_existing or col in seen_remaining:
            continue
        if col in df_sst.columns:
            remaining_columns.append(col)
            seen_remaining.add(col)
    ordered_columns = preferred_existing + remaining_columns
    df_sst = df_sst[ordered_columns]
    df_sst.name = "SST"
    return df_sst


def create_h5_from_json(
    json_path: str | Path,
    h5_path: str | Path | None = None,
    ses_version: str = "IP",
) -> tuple[Path, dict[str, Any]]:
    """Read SES JSON and write an H5 file with SSA/SST dataframes.

    Returns:
        (created_h5_path, diagnostics)
    """
    source_path = Path(json_path)
    data_dictionary, diagnostics = read_json_to_dict(source_path)
    df_ssa = create_ssa_dataframe(data_dictionary)
    df_sst = create_sst_dataframe(data_dictionary)

    if h5_path is None:
        output_base_path = source_path
    else:
        output_base_path = Path(h5_path)

    data = {"SSA": df_ssa}
    if not df_sst.empty:
        data["SST"] = df_sst
    output_meta_data: dict[str, Any] = {
        "file_path": output_base_path,
        "source_file_path": str(source_path),
        "source_file_type": "json",
        "ses_version": ses_version,
        "SES_version": ses_version,
    }
    NO_file_tools.save_h5_file(data, output_meta_data)
    return output_base_path.with_suffix(".h5"), diagnostics


def convert_h5_ip_to_si_and_save_outputs(
    h5_path: str | Path,
    create_excel: bool = True,
) -> tuple[Path, Path | None]:
    """Convert an H5 dataset from IP to SI and save converted H5 and Excel.

    Returns:
        (converted_h5_path, converted_excel_path_or_none)
    """
    source_h5_path = Path(h5_path)
    data, output_meta_data = NO_file_tools.read_h5_file(source_h5_path)

    # JSON-created H5 files may not have ses_version; assume IP for this workflow.
    output_meta_data.setdefault("ses_version", "IP")
    output_meta_data["SES_version"] = output_meta_data.get("ses_version", "IP")

    data, output_meta_data = NO_conversion.convert_output_units(
        "IP_TO_SI",
        data,
        output_meta_data,
    )
    output_meta_data["SES_version"] = output_meta_data.get("ses_version", "IP")

    NO_file_tools.save_h5_file(data, output_meta_data, settings={})
    converted_h5_path = NO_file_tools.get_results_path2(output_meta_data, ".h5")

    converted_excel_path: Path | None = None
    if create_excel:
        NO_Excel_R01.create_excel({}, data, output_meta_data)
        converted_excel_path = NO_file_tools.get_results_path2(
            output_meta_data,
            ".xlsx",
        )

    return converted_h5_path, converted_excel_path


def create_ip_to_si_outputs_from_json(
    json_path: str | Path,
    h5_path: str | Path | None = None,
    create_excel: bool = True,
) -> tuple[Path, Path, Path | None, dict[str, Any]]:
    """Create JSON H5, then convert that H5 from IP to SI and save outputs.

    Returns:
        (created_h5_path, converted_h5_path, converted_excel_path_or_none, diagnostics)
    """
    created_h5_path, diagnostics = create_h5_from_json(
        json_path,
        h5_path=h5_path,
        ses_version="IP",
    )
    converted_h5_path, converted_excel_path = convert_h5_ip_to_si_and_save_outputs(
        created_h5_path,
        create_excel=create_excel,
    )
    return created_h5_path, converted_h5_path, converted_excel_path, diagnostics


def run_json_to_si_outputs(
    json_path: str | Path,
    h5_path: str | Path | None = None,
    create_excel: bool = True,
) -> tuple[Path, Path, Path | None, dict[str, Any]]:
    """Main-style workflow entry point for JSON -> SI outputs.

    This is a top-level orchestrator that:
    1) builds an IP-tagged H5 from JSON,
    2) converts that H5 to SI,
    3) optionally writes SI Excel output.
    """
    return create_ip_to_si_outputs_from_json(
        json_path=json_path,
        h5_path=h5_path,
        create_excel=create_excel,
    )


def _print_summary(diagnostics: dict[str, Any], verbose: bool = False) -> None:
    print(f"file_path: {diagnostics.get('file_path', '')}")
    print(f"top_level_type: {diagnostics.get('top_level_type', '')}")
    print(f"record_count: {diagnostics.get('record_count', 0)}")
    print(f"pit_record_count: {diagnostics.get('pit_record_count', 0)}")
    print(f"info_present: {diagnostics.get('info_present', False)}")
    print(f"warning_count: {diagnostics.get('warning_count', 0)}")

    top_level_keys = diagnostics.get("top_level_keys", [])
    if top_level_keys:
        print(f"top_level_keys: {', '.join(top_level_keys)}")

    sample_pit_keys = diagnostics.get("sample_pit_keys", [])
    if sample_pit_keys:
        print(f"sample_pit_keys: {', '.join(sample_pit_keys)}")

    if verbose:
        for warning in diagnostics.get("warnings", []):
            print(f"warning: {warning}")


def _build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Read SES JSON into native Python objects and report lightweight diagnostics."
        )
    )
    parser.add_argument("json_path", help="Path to SES JSON file")
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print all warnings about optional/missing keys",
    )
    parser.add_argument(
        "--create-h5",
        action="store_true",
        help="Create an H5 file containing SSA/SST dataframes from the JSON input",
    )
    parser.add_argument(
        "--h5-path",
        default=None,
        help="Optional output path for H5. If omitted, uses JSON filename with .h5 suffix.",
    )
    return parser


def main() -> int:
    args = _build_argument_parser().parse_args()
    try:
        data_dictionary, diagnostics = read_json_to_dict(args.json_path)
    except JsonParserError as exc:
        print(f"error: {exc}")
        return 1

    _print_summary(diagnostics, verbose=args.verbose)
    df_ssa = create_ssa_dataframe(data_dictionary)
    df_sst = create_sst_dataframe(data_dictionary)
    print(f"ssa_shape: {df_ssa.shape}")
    if not df_ssa.empty:
        print(f"ssa_columns: {', '.join(df_ssa.columns)}")
    print(f"sst_shape: {df_sst.shape}")
    if not df_sst.empty:
        print(f"sst_columns: {', '.join(df_sst.columns)}")

    if args.create_h5:
        created_h5_path, _ = create_h5_from_json(
            args.json_path,
            h5_path=args.h5_path,
            ses_version="IP",
        )
        print(f"h5_created: {created_h5_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
