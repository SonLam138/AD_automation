# App/Resolver/Email/hr_form_parser.py

import re

from text_utils import (
    remove_accents,
    normalize_text_value
)


class HREmailParser:

    def parse(self, email_body: str) -> dict:

        full_name = self.extract_field(
            email_body,
            "Họ và tên"
        )

        employee_id = self.extract_field(
            email_body,
            "Mã nhân viên"
        )

        birth_date = self.extract_field(
            email_body,
            "Ngày Sinh"
        )

        title = self.extract_field(
            email_body,
            "Chức danh"
        )

        position = self.extract_field(
            email_body,
            "Vị trí"
        )

        department_line = self.extract_field(
            email_body,
            "Phòng/Ban"
        )

        division_name = self.extract_field(
            email_body,
            "Khối"
        )

        department_name = self.build_department_name(
            department_line
        )

        unit_hint = self.build_unit_hint(
            department_line=department_line,
            division_name=division_name
        )

        employee_extract = {
            "full_name": normalize_text_value(full_name),
            "employee_id": employee_id.strip(),
            "birth_date": birth_date.strip(),
            "title": normalize_text_value(title),
            "position": normalize_text_value(position),
            "division_name": normalize_text_value(
                division_name
            ),
            "org_line": normalize_text_value(department_line),
            "department_name": normalize_text_value(
                department_name
            ),
            "unit_hint": normalize_text_value(
                unit_hint
            )
        }

        return employee_extract

    def extract_field(
        self,
        email_body: str,
        field_name: str
    ) -> str:

        pattern = rf"{re.escape(field_name)}\s*:\s*(.+)"

        match = re.search(
            pattern,
            email_body,
            re.IGNORECASE
        )

        if not match:
            return ""

        return match.group(1).strip()

    def build_department_name(
        self,
        department_line: str
    ) -> str:
        """
        Rule:

        PVcomBank Khanh Hoa
        - Phong Khach Hang Ca Nhan
        - Bo Phan Khach Hang Ca Nhan

        --> Phong Khach Hang Ca Nhan

        Trung tam du lieu
        - Phong Tu Dong hoa

        --> Phong Tu Dong hoa
        """

        if not department_line:
            return ""

        segments = [
            seg.strip()
            for seg in department_line.split("-")
            if seg.strip()
        ]

        for segment in segments:

            normalized = remove_accents(
                segment
            ).lower()

            if normalized.startswith("phong "):
                return segment

        return ""

    def build_unit_hint(
        self,
        department_line: str,
        division_name: str
    ) -> str:
        """
        Business Rule

        Nếu có segment chứa PVcomBank
            -> lấy segment đó

        Ngược lại
            -> dùng division_name
        """

        if not department_line:
            return division_name

        segments = [
            seg.strip()
            for seg in department_line.split("-")
            if seg.strip()
        ]

        for segment in segments:

            normalized = remove_accents(
                segment
            ).lower()

            if normalized.startswith("pvcombank"):
                return segment

        return division_name