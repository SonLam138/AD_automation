from fastapi import FastAPI

from app.api.auth import router as auth_router
from app.api.admin import router as admin_router
from app.api.users import router as user_router
from app.api.create_user import router as create_user_router

app = FastAPI(
    title="AD Capability Service"
)

app.include_router(
    auth_router,
    prefix="/auth",
    tags=["Authentication"]
)

app.include_router(
    admin_router,
    prefix="/admin",
    tags=["Admin"]
)

app.include_router(
    user_router,
    prefix="/admin/users",
    tags=["Users"]
)

app.include_router(
    create_user_router,
    prefix="/admin/users",
    tags=["User Management"]
)