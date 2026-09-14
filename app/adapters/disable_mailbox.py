import json
import subprocess
from pathlib import Path


def execute(identity: str):

    ps_script = Path(
        r".\app\adapters\exchange_connection.ps1"
    ).resolve()

    command = f'''
Disable-Mailbox -Identity "{identity}" -Confirm:$false

@{{
    Success = $true
    Identity = "{identity}"
}} | ConvertTo-Json
'''

    result = subprocess.run(
        [
            "powershell",
            "-ExecutionPolicy", "Bypass",
            "-File", str(ps_script),
            command
        ],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        raise Exception(result.stderr)

    return json.loads(result.stdout)