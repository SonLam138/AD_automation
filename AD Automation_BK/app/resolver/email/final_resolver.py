# App/Resolver/Email/final_resolver.py
import json
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent

DIVISION_CODE_MAP_FILE = (
    CURRENT_DIR
    / "division_code_map.json"
)


class FinalResolver:
    """
    Round 2 deterministic resolver.

    Input:
        - round1_extract: output from HREmailParser
        - search_result: output from ExcelOrganizationLookupTool / search_tool

    Output:
        - final resolved data for pending_request
    """
    def __init__(self):
        self.division_code_map = (
            self.load_division_code_map()
        )

    def load_division_code_map(self) -> dict:
        """
        Load division code mapping from JSON config.

        This keeps division-code knowledge outside Python code.
        Update division_code_map.json when organization codes change.
        """

        if not DIVISION_CODE_MAP_FILE.exists():
            raise FileNotFoundError(
                f"Division code map file not found: "
                f"{DIVISION_CODE_MAP_FILE}"
            )

        with open(
            DIVISION_CODE_MAP_FILE,
            "r",
            encoding="utf-8"
        ) as f:
            data = json.load(f)

        if not isinstance(data, dict):
            raise ValueError(
                "division_code_map.json must contain a JSON object"
            )

        return data


    def resolve(
        self,
        round1_extract: dict,
        search_result: dict
    ) -> dict:

        full_name = round1_extract.get("full_name", "").strip()
        division_name = round1_extract.get("division_name", "").strip()

        first_name = self.build_first_name(full_name)
        last_name = self.build_last_name(full_name)
        sam_account_name = self.build_sam_account_name(full_name)

        division_code = self.build_division_code(division_name)
        unit_code = self.get_unit_code(search_result)

        display_name = self.build_display_name(
            full_name=full_name,
            division_code=division_code,
            unit_code=unit_code
        )

        resolved_data = {
            # Identity from Round 1
            "full_name": full_name,
            "employee_id": round1_extract.get("employee_id", ""),
            "birth_date": round1_extract.get("birth_date", ""),
            "title": round1_extract.get("title", ""),
            "position": round1_extract.get("position", ""),

            # Organization from Round 1
            "division_name": division_name,
            "department_name": round1_extract.get("department_name", ""),
            "unit_hint": round1_extract.get("unit_hint", ""),

            # Account attributes resolved in Round 2
            "first_name": first_name,
            "last_name": last_name,
            "display_name": display_name,
            "sam_account_name": sam_account_name,

            # AD mapping from Tool
            "target_ou": search_result.get("target_ou", ""),
            "group_name": search_result.get("group_name", ""),

            # Tool metadata
            "unit_name": search_result.get("unit_name", ""),
            "unit_type": search_result.get("unit_type", ""),
            "unit_code": unit_code,
            "lookup_matched": search_result.get("matched", False),
            "lookup_confidence": search_result.get("confidence", 0),

            # Resolver metadata
            "resolver_mode": "DETERMINISTIC",
            "resolver_round": "ROUND_2_FINAL_RESOLVE",
            "llm_used": False,

            # Reasoning for audit/debug
            "resolve_reasoning": {
                "round1_source": "hr_email_parser",
                "tool_source": "search_tool",
                "display_name_rule": (
                    "display_name = full_name + "
                    "' (' + division_code + '-' + unit_code + ')'"
                ),
                "division_code_source": "division_name",
                "unit_code_source": "search_result.unit_code",
                "sam_account_rule": (
                    "sam_account_name = given_name + initials of family/middle names"
                )
            }
        }

        resolved_data["resolve_status"] = self.build_resolve_status(
            resolved_data
        )

        return resolved_data

    def build_first_name(self, full_name: str) -> str:
        """
        Nguyen Minh Son
        -> Son

        Nguyen Thi Hong Van
        -> Van
        """

        parts = self.split_name(full_name)

        if not parts:
            return ""

        return parts[-1]

    def build_last_name(self, full_name: str) -> str:
        """
        Nguyen Minh Son
        -> Nguyen Minh

        Nguyen Thi Hong Van
        -> Nguyen Thi Hong
        """

        parts = self.split_name(full_name)

        if len(parts) <= 1:
            return ""

        return " ".join(parts[:-1])

    def build_sam_account_name(self, full_name: str) -> str:
        """
        Default deterministic sAMAccountName.

        Nguyen Minh Son
        -> SonNM

        Nguyen Thi Hong Van
        -> VanNTH

        Vu Kim Van Tuyen
        -> TuyenVKV

        Duplicate handling is NOT done here.
        AD creation layer will decide final unique account.
        """

        parts = self.split_name(full_name)

        if not parts:
            return ""

        if len(parts) == 1:
            return parts[0]

        given_name = parts[-1]

        initials = ""
        for word in parts[:-1]:
            if word:
                initials += word[0].upper()

        return f"{given_name}{initials}"

    def build_display_name(
        self,
        full_name: str,
        division_code: str,
        unit_code: str
    ) -> str:
        """
        DisplayName format:

        Ho va ten (K.<division_code>-<unit_code>)

        Examples:
            Nguyen Minh Son (K.CNTT-HO)
            Nguyen Van A (K.CNTT-HCM)
            Nguyen Thi B (K.KHCN-AGG)
        """

        if not full_name:
            return ""

        if not division_code and not unit_code:
            return full_name

        if not division_code:
            return f"{full_name} ({unit_code})"

        if not unit_code:
            return f"{full_name} ({division_code})"

        return f"{full_name} ({division_code}-{unit_code})"

    def build_division_code(
        self,
        division_name: str
    ) -> str:
        """
        Resolve division code from external JSON config.

        Example:
            Khoi Cong Nghe Thong Tin
            -> K.CNTT

            Khoi Khach Hang Ca Nhan
            -> K.KHCN
        """

        if not division_name:
            return ""

        division_name = division_name.strip()

        division_code = self.division_code_map.get(
            division_name
        )

        if division_code:
            return division_code

        return self.build_division_code_fallback(
            division_name
        )

    def get_unit_code(self, search_result: dict) -> str:
        """
        unit_code comes from search_tool.

        Examples:
            HO
            HCM
            AGG
            KHA
        """

        unit_code = search_result.get("unit_code", "")

        if not unit_code:
            return ""

        return str(unit_code).strip().upper()

    def split_name(self, value: str) -> list:
        if not value:
            return []

        return [
            part.strip()
            for part in value.split()
            if part.strip()
        ]

    def build_resolve_status(self, resolved_data: dict) -> dict:
        """
        Validate required fields for final pending request.
        """

        required_fields = [
            "full_name",
            "employee_id",
            "display_name",
            "first_name",
            "last_name",
            "sam_account_name",
            "division_name",
            "department_name",
            "unit_hint",
            "target_ou",
            "group_name",
            "unit_code",
        ]

        missing_fields = []

        for field in required_fields:
            value = resolved_data.get(field)

            if value is None or value == "":
                missing_fields.append(field)

        return {
            "success": len(missing_fields) == 0,
            "missing_fields": missing_fields
        }