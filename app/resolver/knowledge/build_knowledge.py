import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

import pandas as pd


BUILDER_VERSION = "1.0.0"


REQUIRED_COLUMNS = [
    "Division/Branch Name",
    "Department",
    "Group",
    "Branch code",
    "OUName",
]


def _clean(value) -> str:
    """
    Normalize cell value from Excel.
    Preserve business text, only remove surrounding whitespace.
    """
    if pd.isna(value):
        return ""

    return str(value).strip()


def _normalize_key(value: str) -> str:
    """
    Internal key for de-duplication.
    Do not use this as display value.
    """
    return _clean(value).lower()


def _detect_unit_type(unit_name: str, branch_code: str) -> str:
    """
    Detect whether a row belongs to a Division or Branch.

    Current business assumption:
    - Branch normally starts with 'PVcomBank'
    - HO units like 'Khoi ...', 'Ban ...' are divisions
    """
    name = _clean(unit_name)

    if name.lower().startswith("pvcombank"):
        return "branch"

    return "division"


def _extract_ou_label(ou_dn: str) -> str:
    """
    Extract first OU label from DN for LLM readability.

    Example:
    OU=PVCB An Giang,OU=CN-Azure,...
    -> PVCB An Giang
    """
    ou_dn = _clean(ou_dn)

    if not ou_dn:
        return ""

    first_part = ou_dn.split(",")[0].strip()

    if first_part.upper().startswith("OU="):
        return first_part[3:].strip()

    return first_part


def _ensure_required_columns(df: pd.DataFrame) -> None:
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]

    if missing:
        raise ValueError(
            f"Missing required columns in mapping file: {missing}. "
            f"Expected columns: {REQUIRED_COLUMNS}"
        )


def _add_department(parent: Dict[str, Any], department_name: str) -> None:
    """
    Add department under division/branch if not exists.
    Department belongs to its parent unit, not global organization.
    """
    department_name = _clean(department_name)

    if not department_name:
        return

    existing = {
        _normalize_key(item["name"])
        for item in parent.get("departments", [])
    }

    if _normalize_key(department_name) not in existing:
        parent.setdefault("departments", []).append({
            "name": department_name
        })


def build_knowledge_catalog(
    input_file: str,
    output_file: str,
    knowledge_version: str = "1.0.0",
) -> Dict[str, Any]:
    """
    Build resolver knowledge catalog from Excel/CSV mapping file.

    Input columns:
    - Division/Branch Name
    - Department
    - Group
    - Branch code
    - OUName

    Output:
    - organization.divisions[]
    - organization.branches[]
    - resource_catalog.ou_catalog[]
    - resource_catalog.group_catalog[]
    - examples[]
    """

    input_path = Path(input_file)
    output_path = Path(output_file)

    if not input_path.exists():
        raise FileNotFoundError(f"Input mapping file not found: {input_path}")

    if input_path.suffix.lower() in [".xlsx", ".xls"]:
        df = pd.read_excel(input_path, engine="openpyxl")
    elif input_path.suffix.lower() == ".csv":
        df = pd.read_csv(input_path)
    else:
        raise ValueError(
            f"Unsupported file format: {input_path.suffix}. "
            "Supported formats: .xlsx, .xls, .csv"
        )

    _ensure_required_columns(df)

    divisions_by_key: Dict[str, Dict[str, Any]] = {}
    branches_by_key: Dict[str, Dict[str, Any]] = {}

    ou_by_key: Dict[str, Dict[str, Any]] = {}
    group_by_key: Dict[str, Dict[str, Any]] = {}

    examples: List[Dict[str, Any]] = []

    for _, row in df.iterrows():
        unit_name = _clean(row["Division/Branch Name"])
        department_name = _clean(row["Department"])
        group_name = _clean(row["Group"])
        branch_code = _clean(row["Branch code"])
        ou_dn = _clean(row["OUName"])

        if not unit_name and not department_name and not group_name and not ou_dn:
            continue

        unit_type = _detect_unit_type(unit_name, branch_code)

        if unit_type == "branch":
            unit_key = _normalize_key(f"{branch_code}|{unit_name}")

            if unit_key not in branches_by_key:
                branches_by_key[unit_key] = {
                    "name": unit_name,
                    "code": branch_code,
                    "departments": []
                }

            _add_department(
                branches_by_key[unit_key],
                department_name
            )

        else:
            unit_key = _normalize_key(f"{branch_code}|{unit_name}")

            if unit_key not in divisions_by_key:
                divisions_by_key[unit_key] = {
                    "name": unit_name,
                    "branch_code": branch_code,
                    "departments": []
                }

            _add_department(
                divisions_by_key[unit_key],
                department_name
            )

        if ou_dn:
            ou_key = _normalize_key(ou_dn)

            if ou_key not in ou_by_key:
                ou_by_key[ou_key] = {
                    "ou_dn": ou_dn,
                    "ou_label": _extract_ou_label(ou_dn)
                }

        if group_name:
            group_key = _normalize_key(group_name)

            if group_key not in group_by_key:
                group_by_key[group_key] = {
                    "group_name": group_name
                }

        examples.append({
            "unit_type": unit_type,
            "division_branch_name": unit_name,
            "branch_code": branch_code,
            "department": department_name,
            "group": group_name,
            "target_ou": ou_dn
        })

    knowledge = {
        "metadata": {
            "version": knowledge_version,
            "generated_at": datetime.now().isoformat(timespec="seconds"),
            "source_file": str(input_path),
            "builder_version": BUILDER_VERSION,
            "description": (
                "Knowledge catalog for AD Automation Resolver. "
                "Generated from Division/Branch, Department, Group, Branch code, and OU mapping file."
            )
        },

        "organization": {
            "divisions": list(divisions_by_key.values()),
            "branches": list(branches_by_key.values())
        },

        "resource_catalog": {
            "ou_catalog": list(ou_by_key.values()),
            "group_catalog": list(group_by_key.values())
        },

        "examples": examples
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(
            knowledge,
            f,
            ensure_ascii=False,
            indent=2
        )

    return knowledge


if __name__ == "__main__":
    build_knowledge_catalog(
        input_file=f"D:\AD Automation\\app\\resolver\knowledge\source\mapping.xlsx",
        output_file=f"D:\AD Automation\\app\\resolver\knowledge\knowledge_v1.json",
        knowledge_version="1.0.0"
    )