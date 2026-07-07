# from urllib import request

# from fastapi import APIRouter
# from fastapi import Depends
# from fastapi import HTTPException

# from app.models.session_context import (
#     AuditSessionContext,
#     SessionRequested,
#     SessionActual
# )
# from datetime import datetime
# from app.models.user import CreateUserRequest

# from app.auth.rbac import require_role

# from app.adapters.ldap_adapter import LDAPAdapter

# from app.config import *
# from app.core.session import generate_session_id

# router = APIRouter()

# ldap = LDAPAdapter()

# ldap.connect(
#     LDAP_HOST,
#     LDAP_USER,
#     LDAP_PASSWORD
# )



# @router.post("/create")
# def create_user(
#     request: CreateUserRequest,

#     current_user=Depends(
#         require_role(
#             [
#                 "ad.operator",
#                 "ad.admin"
#             ]
#         )
#     )
# ):
#     session_id = (
#         generate_session_id()
#     )
#     started_at = datetime.utcnow()

#     session_context = AuditSessionContext(

#         schema_version="1.0",

#         session_id=session_id,

#         event_category="IDENTITY",

#         event_type="ONBOARDING",

#         source_type="MANUAL",

#         source_id=None,

#         capability="create_user",

#         status="RUNNING",

#         started_at=started_at,

#         requested=SessionRequested(

#             employee_id=request.employee_id,

#             first_name=request.first_name,

#             last_name=request.last_name,

#             full_name=request.full_name,

#             department=request.department,

#             title=request.title,

#             account=request.sam_account_name,

#             display_name=request.full_name,

#             ou=request.target_ou_dn
#         ),

#         actual=SessionActual()
#     )

#     requested_account = (
#         request.sam_account_name
#     )
#     actual_account = (
#         ldap.find_available_sam(
#             LDAP_BASE_DN,
#             request.sam_account_name
#         )
#     )
#     # Add context to the session_context
#     session_context.actual.account = (actual_account)

#     actual_display_name = (
#     ldap.find_available_display_name(
#         LDAP_BASE_DN,
#         request.full_name
#     )
# )
#     # Add context to the session_context
#     session_context.actual.display_name = (actual_display_name)

#     # Gán lại giá trị sau khi chống duplicate
#     request.display_name = (
#         actual_display_name
#     )

#     request.sam_account_name = (
#         actual_account
#     )

#     user_dn = ldap.build_user_dn(
#     request.display_name,
#     request.target_ou_dn
# )
#     # Add context to the session_context
#     session_context.actual.user_dn = (user_dn)
#     upn = (
#         f"{actual_account}"
#         "@automate.com.vn"
#     )
#     session_context.actual.ou_dn = (
#     request.target_ou_dn
# )
#     if request.dry_run:

#         return {

#             "dry_run": True,

#             "session_id":
#                 session_id,

#             "capability":
#                 "create_user",

#             "requested_account":
#                 requested_account,

#             "actual_account":
#                 actual_account,

#             "will_create_dn":
#                 user_dn,

#             "attributes": {

#                 "displayName":
#                     request.display_name,

#                 "sAMAccountName":
#                     actual_account,

#                 "userPrincipalName":
#                     upn,

#                 "title":
#                     request.title,

#                 "department":
#                     request.department,

#                 "description":
#                     request.description
#             }
#         }
#     print("FULL_NAME:", request.full_name)
#     print("DISPLAY_NAME:", request.display_name)
#     result = ldap.create_user(
#         request,
#         session_id
#     )

#     if not result["success"]:
#         completed_at = datetime.utcnow()

#         session_context.status = "FAILED"

#         session_context.completed_at = (
#             completed_at
#         )

#         session_context.duration_ms = int(
#             (
#                 completed_at -
#                 started_at
#             ).total_seconds() * 1000
#         )

#         session_context.failure_stage = (
#             "create_user"
#         )

#         session_context.failure_code = str(
#             ldap.connection.result.get(
#                 "result"
#             )
#         )

#         session_context.failure_reason = str(
#             ldap.connection.result.get(
#                 "description"
#             )
#         )
#         print(
#             session_context.model_dump_json(
#                 indent=2
#             )
#         )
#         raise HTTPException(
#             status_code=500,
#             detail=str(
#                 ldap.connection.result
#             )
#         )



#     completed_at = datetime.utcnow()

#     session_context.status = "SUCCESS"

#     session_context.completed_at = (
#         completed_at
#     )

#     session_context.duration_ms = int(
#         (
#             completed_at -
#             started_at
#         ).total_seconds() * 1000
#     )
#     print(
#         session_context.model_dump_json(
#             indent=2
#         )
#     )
#     for step in result["session_steps"]:

#         print(
#             step.model_dump_json(
#                 indent=2
#             )
#         )
#     return {

#         "success": True,

#         "session_id":
#             session_id,

#         "capability":
#             "create_user",

#         "requested_account":
#             requested_account,

#         "actual_account":
#             actual_account,
        
#         "DisplayName":
#             actual_display_name,

#         "title":
#             request.title,

#         "department":
#             request.department,

#         "status":
#             "completed"
#     }
    