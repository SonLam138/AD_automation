import unicodedata
from pathlib import Path
from difflib import SequenceMatcher
from typing import Dict, Any, List, Optional

import pandas as pd


DEFAULT_EXCEL_FILE = (
    Path(__file__)
    .resolve()
    .parents[1]
    / "knowledge"
    / "source"
    / "mapping.xlsx"
)


DEFAULT_COLUMNS = [
    "Division/Branch Name",
    "Department",
    "Group",
    "Branch code",
    "OUName",
]


def clean_value(value) -> str:
    if pd.isna(value):
        return ""

    if value is None:
        return ""

    return str(value).strip()


def remove_accents(value: str) -> str:
    value = unicodedata.normalize(
        "NFD",
        value
    )

    return "".join(
        ch for ch in value
        if unicodedata.category(ch) != "Mn"
    )


def normalize_text(value: str) -> str:
    value = clean_value(value).lower()
    value = remove_accents(value)

    replacements = {
        "pvcombank": "",
        "pvcom bank": "",
        "phong": "",
        "bo phan": "",
        "chi nhanh": "",
        "khoi": "",
        "ban": "",
        "-": " ",
        "_": " ",
        ".": " ",
        "/": " "
    }

    for old, new in replacements.items():
        value = value.replace(
            old,
            new
        )

    value = " ".join(
        value.split()
    )

    return value


def similarity(
    left: str,
    right: str
) -> float:
    left_norm = normalize_text(left)
    right_norm = normalize_text(right)

    if not left_norm or not right_norm:
        return 0.0

    if left_norm == right_norm:
        return 1.0

    if left_norm in right_norm or right_norm in left_norm:
        return 0.92

    return SequenceMatcher(
        None,
        left_norm,
        right_norm
    ).ratio()


def detect_unit_type(unit_name: str) -> str:
    unit_norm = normalize_text(unit_name)

    # Sau normalize, "PVcomBank An Giang" còn lại "an giang"
    # Vì vậy detect bằng raw text sẽ chắc hơn.
    raw = clean_value(unit_name).lower()

    if raw.startswith("pvcombank"):
        return "branch"

    return "division"


class ExcelOrganizationLookupTool:
    """
    Excel-based deterministic lookup tool.

    Source of truth:
    - mapping.xlsx

    Excel schema:
    - Division/Branch Name
    - Department
    - Group
    - Branch code
    - OUName

    Tool responsibility:
    - Nhận unit_hint + department_hint
    - Tìm row phù hợp nhất
    - Trả OU, group, unit_code

    Không dùng LLM.
    Không build JSON.
    Không resolve business ngoài Excel.
    """

    def __init__(
        self,
        excel_file: Optional[str] = None,
        sheet_name: Optional[str] = None
    ):
        self.excel_file = (
            Path(excel_file)
            if excel_file
            else DEFAULT_EXCEL_FILE
        )

        self.sheet_name = sheet_name

        self.rows = self._load_rows()

    def _read_excel(self) -> pd.DataFrame:
        if not self.excel_file.exists():
            raise FileNotFoundError(
                f"Excel mapping file not found: {self.excel_file}"
            )

        df = pd.read_excel(
            self.excel_file,
            sheet_name=self.sheet_name,
            engine="openpyxl"
        )

        # Nếu sheet_name=None, pandas trả dict sheet.
        # Ta lấy sheet đầu tiên.
        if isinstance(df, dict):
            first_sheet_name = list(df.keys())[0]
            df = df[first_sheet_name]

        df.columns = [
            str(col).strip()
            for col in df.columns
        ]

        has_named_columns = all(
            col in df.columns
            for col in DEFAULT_COLUMNS
        )

        if has_named_columns:
            return df[DEFAULT_COLUMNS].copy()

        # Fallback cho file không có header đúng tên:
        # lấy 5 cột đầu tiên theo đúng thứ tự kỹ thuật anh đang dùng.
        if len(df.columns) < 5:
            raise ValueError(
                "Mapping file must contain at least 5 columns: "
                "Division/Branch Name, Department, Group, Branch code, OUName"
            )

        df = df.iloc[:, 0:5].copy()
        df.columns = DEFAULT_COLUMNS

        return df

    def _load_rows(self) -> List[Dict[str, Any]]:
        df = self._read_excel()

        rows: List[Dict[str, Any]] = []

        for _, row in df.iterrows():
            unit_name = clean_value(
                row["Division/Branch Name"]
            )

            department_name = clean_value(
                row["Department"]
            )

            group_name = clean_value(
                row["Group"]
            )

            branch_code = clean_value(
                row["Branch code"]
            )

            ou_name = clean_value(
                row["OUName"]
            )

            if not unit_name and not department_name:
                continue

            rows.append(
                {
                    "unit_name": unit_name,
                    "unit_type": detect_unit_type(
                        unit_name
                    ),
                    "unit_code": branch_code,
                    "department_name": department_name,
                    "group_name": group_name,
                    "target_ou": ou_name
                }
            )

        return rows

    def lookup(
        self,
        unit_hint: str,
        department_hint: str,
        debug: bool = False
    ) -> Dict[str, Any]:

        unit_hint = clean_value(unit_hint)
        department_hint = clean_value(department_hint)

        candidates: List[Dict[str, Any]] = []

        for row in self.rows:

            unit_score = similarity(
                unit_hint,
                row["unit_name"]
            )

            department_score = similarity(
                department_hint,
                row["department_name"]
            )

            total_score = (
                unit_score * 0.55
                +
                department_score * 0.45
            )

            candidates.append(
                {
                    "score": round(
                        total_score,
                        4
                    ),
                    "unit_score": round(
                        unit_score,
                        4
                    ),
                    "department_score": round(
                        department_score,
                        4
                    ),
                    "unit_name": row["unit_name"],
                    "unit_type": row["unit_type"],
                    "unit_code": row["unit_code"],
                    "department_name": row["department_name"],
                    "group_name": row["group_name"],
                    "target_ou": row["target_ou"]
                }
            )

        candidates = sorted(
            candidates,
            key=lambda item: item["score"],
            reverse=True
        )

        best_match = (
            candidates[0]
            if candidates
            else None
        )

        if not best_match:
            result = {
                "matched": False,
                "confidence": 0,
                "unit_name": "",
                "unit_type": "",
                "unit_code": "",
                "department_name": "",
                "target_ou": "",
                "group_name": ""
            }

            if debug:
                result["debug_candidates"] = []

            return result

        result = {
            "matched": best_match["score"] >= 0.65,
            "confidence": best_match["score"],

            "unit_name": best_match["unit_name"],
            "unit_type": best_match["unit_type"],
            "unit_code": best_match["unit_code"],

            "department_name": best_match["department_name"],
            "target_ou": best_match["target_ou"],
            "group_name": best_match["group_name"]
        }

        if debug:
            result["debug_candidates"] = candidates[:5]

        return result
    def lookup_from_org_line(
        self,
        org_line: str,
        debug: bool = False
    ) -> Dict[str, Any]:

        org_line = clean_value(org_line)

        parts = [
            item.strip()
            for item in org_line.split("-")
            if item.strip()
        ]

        if len(parts) >= 2:
            unit_hint = parts[0]

            department_hint = " - ".join(
                parts[1:]
            )
        else:
            unit_hint = org_line
            department_hint = org_line

        return self.lookup(
            unit_hint=unit_hint,
            department_hint=department_hint,
            debug=debug
        )


if __name__ == "__main__":

    import json

    tool = ExcelOrganizationLookupTool()

    result = tool.lookup(
        unit_hint="Khối Công nghệ thông tin",
        department_hint="Phong dich vu khach hang"
    )

    print(
        json.dumps(
            result,
            ensure_ascii=False,
            indent=2
        )
    )