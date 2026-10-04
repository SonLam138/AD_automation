from email_reader import EmlEmailReader
from hr_form_parser import HREmailParser
#from app.resolver.tools.excel_lookup import ExcelOrganizationLookupTool
from final_resolver import FinalResolver
import sys
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
RESOLVER_DIR = CURRENT_DIR.parent

sys.path.append(str(RESOLVER_DIR))

from tools.excel_lookup import ExcelOrganizationLookupTool


reader = EmlEmailReader()
parser = HREmailParser()

emails = reader.read_folder()
lookup_tool = ExcelOrganizationLookupTool()
final_resolver = FinalResolver()

for email in emails:

    employee_extract = parser.parse(
        email["body"]
    )

    print("=" * 100)
    print(employee_extract)

    search_result = lookup_tool.lookup(
        employee_extract["unit_hint"],
        employee_extract["department_name"]
    )

    print(search_result)

    # ROUND 2 - Final deterministic resolve
    resolved_data = final_resolver.resolve(
        round1_extract=employee_extract,
        search_result=search_result
    )

    print("[ROUND 2]")
    print(resolved_data)