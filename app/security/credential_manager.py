# security/credential_manager.py

import base64
import json
from pathlib import Path


class CredentialManager:

    @staticmethod
    def save(
        file_path: str,
        password: str,
    ):

        payload = {
            "password": password
        }

        encoded = base64.b64encode(
            json.dumps(
                payload
            ).encode()
        )

        Path(
            file_path
        ).write_bytes(
            encoded
        )

    @staticmethod
    def load(
        file_path: str,
    ):

        encoded = Path(
            file_path
        ).read_bytes()

        payload = json.loads(
            base64.b64decode(
                encoded
            ).decode()
        )

        return payload