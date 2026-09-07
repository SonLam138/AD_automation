import pandas as pd
from app.ra_soat.off_ra_soat_model import RaSoatOffboardingSourceUser

REQUIRED_COLUMNS = [
    "Mã NV",
    "HỌ VÀ TÊN",
    "NGÀY CHẤM DỨT",
    "Mail nội bộ",
]


def load_excel(file_path: str) -> pd.DataFrame:
    return pd.read_excel(file_path)

def validate_headers(df: pd.DataFrame) -> None:
    missing_columns = [
        column
        for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Thiếu cột bắt buộc: {', '.join(missing_columns)}"
        )

def normalize_email(email: str) -> str:
    return str(email).strip().lower()

def extract_username(email: str) -> str:
    return email.split("@")[0]

def map_row_to_source_user(
    row,
) -> RaSoatOffboardingSourceUser:

    return RaSoatOffboardingSourceUser(
        employee_id=str(row["Mã NV"]).strip(),
        full_name=str(row["HỌ VÀ TÊN"]).strip(),
        effective_time=row["NGÀY CHẤM DỨT"],

        email=row["Mail nội bộ"],
        username=row["Username"],
    )

def map_dataframe_to_source_users(
    df: pd.DataFrame,
) -> list[RaSoatOffboardingSourceUser]:

    users = []

    for _, row in df.iterrows():
        users.append(
            map_row_to_source_user(row)
        )

    return users