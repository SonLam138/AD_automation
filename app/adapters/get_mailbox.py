import json
import subprocess
from pathlib import Path


def execute(identity: str):

    ps_script = Path(
        r".\app\adapters\exchange_connection.ps1"
    ).resolve()

    command = f'''
try {{

    $mailbox = Get-Mailbox `
        -Identity "{identity}" `
        -ErrorAction Stop

    @{{
        success = $true
        found = $true
        data = @{{
            Name = $mailbox.Name
            Alias = $mailbox.Alias
            PrimarySmtpAddress = $mailbox.PrimarySmtpAddress.ToString()
        }}
    }} | ConvertTo-Json -Depth 5

}}
catch {{

    if ($_.Exception.Message -like "*couldn't be found*") {{

        @{{
            success = $true
            found = $false
            data = $null
        }} | ConvertTo-Json -Depth 5

    }}
    else {{

        @{{
            success = $false
            error = $_.Exception.Message
        }} | ConvertTo-Json -Depth 5

    }}

}}
'''

    result = subprocess.run(
        [
            "powershell",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(ps_script),
            command
        ],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        raise Exception(result.stderr)

    stdout = result.stdout.strip()

    if not stdout:
        raise Exception(
            f"Exchange returned empty output. stderr={result.stderr}"
        )

    return json.loads(stdout)