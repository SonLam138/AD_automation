from fastapi import Depends
from fastapi import HTTPException

from app.auth.dependencies import (
    get_current_user
)


def require_group(
    allowed_groups: list[str]
):

    def checker(
        current_user=Depends(
            get_current_user
        )
    ):

        user_groups = current_user.get(
            "groups",
            []
        )

        for group in allowed_groups:

            if group in user_groups:
                return current_user

        raise HTTPException(
            status_code=403,
            detail="Permission denied"
        )

    return checker