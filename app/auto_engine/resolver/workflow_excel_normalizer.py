COLUMN_MAPPING = {

    "employee_id": [
        "employee_id",
        "employeeid",
        "employee id",
        "employee-id",
        "ma nhan vien",
        "mã nhân viên",
        "staff_id"
    ],

    "email": [
        "email",
        "mail",
        "e-mail"
    ],

    "reason": [
        "reason",
        "ly do",
        "lý do"
    ],

    "effective_time": [
        "effective_time",
        "effectived_time",     # HR typo 😎
        "effective date",
        "effective_datetime",
        "ngay hieu luc",
        "ngày hiệu lực"
    ]
}
def normalize_column_name(
    column_name: str
) -> str:

    normalized = (
        str(column_name)
        .strip()
        .lower()
    )

    for canonical_name, aliases in (
        COLUMN_MAPPING.items()
    ):

        if normalized in aliases:
            return canonical_name

    return normalized

def normalize_columns(
    dataframe
):

    dataframe.columns = [

        normalize_column_name(
            column
        )

        for column
        in dataframe.columns

    ]

    return dataframe