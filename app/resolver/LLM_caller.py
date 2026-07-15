import json
import re
import requests
from typing import Any, Dict

from file_loader import (
    load_config,
    load_prompt,
    load_guide
)
from file_loader import load_extract_prompt, load_resolve_prompt
from tools.excel_lookup import ExcelOrganizationLookupTool
from pending_request_builder import (
    build_pending_request_from_resolver_result,
    upsert_pending_request
)

OLLAMA_URL = "http://localhost:11434/api/generate"


class ResolverLLM:
    """
    LLM Resolver orchestrator.

    Flow:
    1. LLM đọc email và extract lookup hint.
    2. Python gọi ExcelOrganizationLookupTool.
    3. LLM nhận tool result và build final resolved JSON.

    Lưu ý:
    - Không nhét Excel/mapping vào prompt.
    - Không nhét knowledge vào context.
    - Tool lookup là deterministic.
    - LLM chỉ xử lý email + kết quả tool.
    """

    def __init__(self):
        self.config = load_config()

        self.extract_prompt = load_extract_prompt(
        self.config[
            "prompt_extract_version"
            ]
        )

        self.resolve_prompt = load_resolve_prompt(
        self.config[
            "prompt_resolve_version"
            ]
        )

        # self.prompt = load_prompt(
        #     self.config["prompt_version"]
        # )

        self.guide = load_guide(
            self.config["guide_version"]
        )

        self.lookup_tool = ExcelOrganizationLookupTool()

    # ============================================================
    # LOW LEVEL OLLAMA CALL
    # ============================================================

    def _call_ollama(
        self,
        full_prompt: str
    ) -> str:

        payload = {
            "model": self.config["model"],
            "prompt": full_prompt,
            "stream": False
        }

        response = requests.post(
            OLLAMA_URL,
            json=payload,
            timeout=500
        )

        response.raise_for_status()

        result = response.json()

        return result.get(
            "response",
            ""
        )

    # ============================================================
    # JSON HELPERS
    # ============================================================

    def _extract_json_text(
        self,
        text: str
    ) -> str:
        """
        Mistral đôi khi trả:
        ```json
        {...}
        ```

        Hàm này cố lấy ra JSON object đầu tiên.
        """

        if not text:
            return ""

        text = text.strip()

        # Remove markdown fence
        text = re.sub(
            r"^```json",
            "",
            text,
            flags=re.IGNORECASE
        ).strip()

        text = re.sub(
            r"^```",
            "",
            text
        ).strip()

        text = re.sub(
            r"```$",
            "",
            text
        ).strip()

        # Extract first JSON object
        start = text.find("{")
        end = text.rfind("}")

        if start != -1 and end != -1 and end > start:
            return text[start:end + 1]

        return text

    def _safe_json_loads(
        self,
        text: str
    ) -> Dict[str, Any]:

        json_text = self._extract_json_text(
            text
        )

        try:
            return json.loads(
                json_text
            )

        except Exception:
            return {
                "_parse_error": True,
                "_raw_output": text
            }

    # ============================================================
    # BUILD PENDING REQUEST
    # ============================================================
    def call_and_create_pending_request(
        self,
        email_text: str,
        debug: bool = True
    ) -> Dict[str, Any]:
        """
        Chạy Resolver V2 đầy đủ:
        Round 1 -> Tool -> Round 2

        Sau đó build Pending Request V2
        và ghi vào app/data/pending_requests.json.
        """

        resolver_result = self.call(
            email_text=email_text,
            debug=debug
        )

        pending_request = build_pending_request_from_resolver_result(
            resolver_result
        )

        upsert_pending_request(
            pending_request
        )

        if debug:
            print("=" * 80)
            print("PENDING REQUEST CREATED")
            print("=" * 80)
            print(
                json.dumps(
                    pending_request,
                    ensure_ascii=False,
                    indent=2
                )
            )

        return {
            "resolver_result": resolver_result,
            "pending_request": pending_request
        }

    # ============================================================
    # ROUND 1: EXTRACT TOOL REQUEST
    # ============================================================

    def build_extract_prompt(
        self,
        email_text: str
    ) -> str:

        return f"""
        {self.extract_prompt}



================ EMAIL CẦN XỬ LÝ ================

{email_text}

================ QUY TRÌNH TẠO THÔNG TIN LOOKUP ================

{self.guide}

"""

    def extract_lookup_request(
        self,
        email_text: str,
        debug: bool = True
    ) -> Dict[str, Any]:

        full_prompt = self.build_extract_prompt(
            email_text
        )

        raw_output = self._call_ollama(
            full_prompt
        )

        parsed = self._safe_json_loads(
            raw_output
        )

        if debug:
            print("=" * 80)
            print("ROUND 1 - RAW OUTPUT")
            print("=" * 80)
            print(raw_output)

            print("=" * 80)
            print("ROUND 1 - PARSED")
            print("=" * 80)
            print(
                json.dumps(
                    parsed,
                    ensure_ascii=False,
                    indent=2
                )
            )

        return parsed

    # ============================================================
    # TOOL CALL
    # ============================================================

    def call_lookup_tool(
        self,
        extract_result: Dict[str, Any],
        debug: bool = True
    ) -> Dict[str, Any]:

        employee_extract = extract_result.get(
            "employee_extract",
            {}
        )

        unit_hint = employee_extract.get(
            "unit_hint",
            ""
        )

        department_hint = employee_extract.get(
            "department_hint",
            ""
        )

        org_line = employee_extract.get(
            "org_line",
            ""
        )

        # Ưu tiên dùng unit_hint + department_hint.
        # Nếu LLM extract yếu thì fallback org_line.
        if unit_hint or department_hint:
            lookup_result = self.lookup_tool.lookup(
                unit_hint=unit_hint,
                department_hint=department_hint,
                debug=False
            )
        else:
            lookup_result = self.lookup_tool.lookup_from_org_line(
                org_line=org_line,
                debug=False
            )

        if debug:
            print("=" * 80)
            print("TOOL RESULT")
            print("=" * 80)
            print(
                json.dumps(
                    lookup_result,
                    ensure_ascii=False,
                    indent=2
                )
            )

        return lookup_result

    # ============================================================
    # ROUND 2: FINAL RESOLVE
    # ============================================================

    def build_final_prompt(
        self,
        email_text: str,
        extract_result: Dict[str, Any],
        lookup_result: Dict[str, Any]
    ) -> str:
        
        return f"""
        {self.resolve_prompt}

================ EMAIL CẦN XỬ LÝ ================

{email_text}

================ EMPLOYEE_EXTRACT ================

{json.dumps(
    extract_result,
    ensure_ascii=False,
    indent=2
)}

================ TOOL_RESULT ================

{json.dumps(
    lookup_result,
    ensure_ascii=False,
    indent=2
)}

================ QUY TRÌNH RESOLVE ================

{self.guide}
"""

    def final_resolve(
        self,
        email_text: str,
        extract_result: Dict[str, Any],
        lookup_result: Dict[str, Any],
        debug: bool = True
    ) -> Dict[str, Any]:

        full_prompt = self.build_final_prompt(
            email_text=email_text,
            extract_result=extract_result,
            lookup_result=lookup_result
        )

        raw_output = self._call_ollama(
            full_prompt
        )

        parsed = self._safe_json_loads(
            raw_output
        )

        if debug:
            print("=" * 80)
            print("ROUND 2 - RAW OUTPUT")
            print("=" * 80)
            print(raw_output)

            print("=" * 80)
            print("ROUND 2 - PARSED")
            print("=" * 80)
            print(
                json.dumps(
                    parsed,
                    ensure_ascii=False,
                    indent=2
                )
            )

        return parsed

    # ============================================================
    # PUBLIC ENTRYPOINT
    # ============================================================

    def call(
        self,
        email_text: str,
        debug: bool = True
    ) -> Dict[str, Any]:

        extract_result = self.extract_lookup_request(
            email_text=email_text,
            debug=debug
        )

        lookup_result = self.call_lookup_tool(
            extract_result=extract_result,
            debug=debug
        )

        final_result = self.final_resolve(
            email_text=email_text,
            extract_result=extract_result,
            lookup_result=lookup_result,
            debug=debug
        )

        return {
            "prompt_version": self.config.get(
                "prompt_version",
                ""
            ),
            "guide_version": self.config.get(
                "guide_version",
                ""
            ),
            "model": self.config.get(
                "model",
                ""
            ),
            "extract_result": extract_result,
            "lookup_result": lookup_result,
            "final_result": final_result
        }


if __name__ == "__main__":

    email_text = """

Kính gửi anh/chị IT Support,

Hệ thống SAP HCM kính gửi các anh/ chị thông tin của CBNV mới Tuyển mới tại PVcomBank với thông tin cụ thể như sau:

Họ và tên : Vũ Kim Vân Tuyền
Mã nhân viên : 00017003
Ngày Sinh : 23/09/2000
Chức danh : Giao dịch viên
Vị trí : Giao dịch viên
Phòng/Ban : PVcomBank Thủ Đức - Phòng Dịch Vụ Khách Hàng
Khối : Khối Khách Hàng Cá Nhân
Lý do của quyết định: Xét tuyển
Kính gửi các anh/chị IT Support tạo tài khoản cho CBNV.
"""

    resolver = ResolverLLM()

    result = resolver.call_and_create_pending_request(
    email_text=email_text,
    debug=True
    )

    print("=" * 80)
    print("FINAL PENDING REQUEST")
    print("=" * 80)

    print(
        json.dumps(
            result["pending_request"],
            ensure_ascii=False,
            indent=2
        )
    )