from enum import Enum


class SourceType(str, Enum):
    UI = "ui"
    EMAIL = "email"
    API = "api"
    EXCEL = "excel"