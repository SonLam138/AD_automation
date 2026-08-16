from typing import Dict
import uuid
from datetime import datetime

from app.auto_engine.models.base import SourceAdapter
from app.auto_engine.models.request_models import Request


class RequestRepository:

    def __init__(self):
        self._requests: Dict[str, SourceAdapter] = {}

    def save(
        self,
        request_id: str,
        request: SourceAdapter
    ):
        self._requests[request_id] = request

    def get(
        self,
        request_id: str
    ):
        return self._requests.get(request_id)


class RequestService:

    def _generate_request_id(self) -> str:

        date_part = datetime.now().strftime("%d%m%Y")

        random_part = uuid.uuid4().hex[:4].upper()

        return f"REQ_{date_part}_{random_part}"
