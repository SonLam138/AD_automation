# security/ldap_credential_provider.py

import subprocess
from pathlib import Path


class LdapCredentialProvider:

    @staticmethod
    def get_password():

        encrypted = (
            Path(
                "app/security/ldap_credential.dat"
            )
            .read_text(
                encoding="utf-8-sig"
            )
            .strip()
        )

        ps_script = f"""
$securePassword =
    "{encrypted}" |
    ConvertTo-SecureString

$BSTR =
    [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR(
        $securePassword
    )

[System.Runtime.InteropServices.Marshal]::PtrToStringAuto(
    $BSTR
)
"""

        result = subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-Command",
                ps_script,
            ],
            capture_output=True,
            text=True,
        )

        return result.stdout.strip()