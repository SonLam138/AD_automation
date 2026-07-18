from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.auth import router as auth_router
from app.api.admin import router as admin_router
from app.api.users import router as user_router
#from app.api.create_user import router as create_user_router
from app.api.new_onboarding import (
    router as onboarding_router
)
from app.api.resolver_fake import router as resolver_fake_router
from app.api.onboarding_request import router as onboarding_request_router
from app.api.tool_ad import router as tool_ad_router
from Onboard_UI.routers.auth_router import router as onboard_ui_router


app = FastAPI(
    title="AD Capability Service"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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

# app.include_router(
#     create_user_router,
#     prefix="/admin/users",
#     tags=["User Management"]
# )

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

app.include_router(
    onboard_ui_router,
    prefix="/onboard_auth",
    tags=["Onboard_Authentication"]
)
app.include_router(
    tool_ad_router,
    prefix="/api/ad",
    tags=["AD Tools"]
)
