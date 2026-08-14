from abc import ABC
from abc import abstractmethod

from .request_models import Request


class SourceAdapter(ABC):

    @abstractmethod
    def parse(self, source_data) -> Request:
        pass