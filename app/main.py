from fastapi import FastAPI

from app.api.auth import router as auth_router
from app.api.admin import router as admin_router
from app.api.users import router as user_router
from app.api.create_user import router as create_user_router
from app.api.new_onboarding import (
    router as onboarding_router
)
from app.api.resolver_fake import router as resolver_fake_router
from app.api.onboarding_request import router as onboarding_request_router

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

app.include_router(
    onboarding_router,
    prefix="/onboarding",
    tags=["Onboarding"]
)
app.include_router(
    resolver_fake_router,
    prefix="/onboarding",
    tags=["Onboarding"]
)

app.include_router(
    onboarding_request_router,
    prefix="/onboarding/requests",
    tags=["Onboarding Requests"]
)
