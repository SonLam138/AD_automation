import shutil
from pathlib import Path
from email_reader import EmlEmailReader
from hr_form_parser import HREmailParser
from final_resolver import FinalResolver

from pending_request_builder import (
    build_pending_request_from_resolver_result,
    upsert_pending_request
)

import sys
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
RESOLVER_DIR = CURRENT_DIR.parent

if str(RESOLVER_DIR) not in sys.path:
    sys.path.append(str(RESOLVER_DIR))

from tools.excel_lookup import (
    ExcelOrganizationLookupTool
)



class AutoOnboardingRuntime:
    DONE_DIR = Path(
    r"D:\AD Automation\Done_DataMail"
    )

    def __init__(self):

        self.reader = EmlEmailReader()

        self.parser = HREmailParser()

        self.lookup_tool = (
            ExcelOrganizationLookupTool()
        )

        self.final_resolver = (
            FinalResolver()
        )

    def move_processed_email(
        self,
        email_data: dict
    ):

        source_file = email_data.get(
            "source_file"
        )

        if not source_file:
            return

        source_path = Path(source_file)

        if not source_path.exists():
            return

        self.DONE_DIR.mkdir(
            parents=True,
            exist_ok=True
        )

        target_path = (
            self.DONE_DIR
            / source_path.name
        )

        shutil.move(
            str(source_path),
            str(target_path)
        )

        print(
            f"[MOVED] "
            f"{source_path.name}"
        )

    def process_email(
        self,
        email_data: dict
    ) -> dict:

        # ROUND 1

        employee_extract = (
            self.parser.parse(
                email_data["body"]
            )
        )

        # TOOL

        lookup_result = (
            self.lookup_tool.lookup(
                unit_hint=
                    employee_extract["unit_hint"],

                department_hint=
                    employee_extract[
                        "department_name"
                    ]
            )
        )

        # ROUND 2

        resolved_data = (
            self.final_resolver.resolve(
                round1_extract=
                    employee_extract,

                search_result=
                    lookup_result
            )
        )

        resolver_result = {

            "extract_result": {
                "employee_extract":
                    employee_extract
            },

            "lookup_result":
                lookup_result,

            "final_result": {
                "resolved_data":
                    resolved_data
            }
        }

        pending_request = (
            build_pending_request_from_resolver_result(
                resolver_result
            )
        )
        upsert_pending_request(
        pending_request
        )
        self.move_processed_email(
        email_data
        )
        print(
        f"[PENDING SAVED] "
        f"{pending_request['request_id']}"
    )

        return pending_request
    
    def run(self):

        emails = self.reader.read_folder()

        print(
            f"Found: {len(emails)} emails"
        )

        for email in emails:

            try:

                pending_request = (
                    self.process_email(
                        email
                    )
                )

                upsert_pending_request(
                    pending_request
                )

                print(
                    f"[SUCCESS] "
                    f"{email['file_name']}"
                )

            except Exception as ex:

                print(
                    f"[ERROR] "
                    f"{email['file_name']}"
                )

                print(ex)


if __name__ == "__main__":

    runtime = AutoOnboardingRuntime()

    runtime.run()

