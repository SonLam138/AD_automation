from ldap3 import Server, Tls
from ldap3 import Connection
from ldap3 import ALL
from ldap3 import MODIFY_REPLACE, MODIFY_ADD
from ldap3.extend.microsoft.modifyPassword import ad_modify_password
import re
import ssl
from app.models.session_step import AuditSessionStep
from datetime import datetime
from app.audit.summary_builder import build_session_summary
from app.models.session_context import (
    AuditSessionContext,
    SessionRequested,
    SessionActual
)

from app.core.session import generate_session_id

from app.config import LDAP_BASE_DN
from app.audit.audit_writer import save_context, save_step, save_summary

class LDAPAdapter:

    def __init__(self):

        self.connection = None

    def connect(
        self,
        host,
        username,
        password,
        port=636
    ):

        tls_config = Tls(
            validate=ssl.CERT_NONE
        )

        server = Server(
            host,
            port=port,
            use_ssl=True,
            #tls=tls_config,
            get_info=ALL
        )

        self.connection = Connection(
            server,
            user=username,
            password=password,
            auto_bind=True
        )

        return self.connection.bound
    
    def search_user(
        self,
        base_dn,
        sam_account_name
    ):
        
        self.connection.search(
            search_base=base_dn,
            search_filter=f"(sAMAccountName={sam_account_name})",
            attributes=["cn","sAMAccountName"]
        )

        return self.connection.entries
    
    def user_exists(
        self,
        base_dn,
        sam_account_name
    ):

        self.connection.search(
            search_base=base_dn,
            search_filter=f"(sAMAccountName={sam_account_name})",
            attributes=["sAMAccountName"]
        )

        return len(self.connection.entries) > 0
    
    def create_user(
        self,
        request,
        approved_by=None,
        approved_name=None,
        approval_type="MANUAL"

    ):
        session_id = generate_session_id()

        started_at = datetime.utcnow()

        session_steps = []

        requested_account = request.sam_account_name

        session_context = AuditSessionContext(

            schema_version="1.0",

            session_id=session_id,

            event_category="IDENTITY",

            event_type="NEW_ONBOARDING",

            source_type="HR_EMAIL_SVD",

            source_id=None,

            capability="new_onboarding",

            approved_by=approved_by,

            approved_name=approved_name,

            edited_by_approver=request.edited_by_approver,

            approval_type=approval_type,

            approval_time=started_at,

            status="RUNNING",

            started_at=started_at,

            requested=SessionRequested(

                employee_id=request.employee_id,

                first_name=request.first_name,

                last_name=request.last_name,

                full_name=request.full_name,

                department=request.department,

                title=request.title,

                account=request.sam_account_name,

                display_name=request.full_name,

                ou=request.target_ou_dn
            ),

            actual=SessionActual()
        )

        def finalize_context(
            status,
            failure_stage=None,
            failure_code=None,
            failure_reason=None
        ):
            completed_at = datetime.utcnow()

            session_context.status = status

            session_context.completed_at = completed_at

            session_context.duration_ms = int(
                (
                    completed_at -
                    session_context.started_at
                ).total_seconds() * 1000
            )

            if failure_stage:
                session_context.failure_stage = failure_stage

            if failure_code:
                session_context.failure_code = str(
                    failure_code
                )

            if failure_reason:
                session_context.failure_reason = str(
                    failure_reason
                )
        
        save_context(
            session_context
        )

        def append_step(
            step_name,
            status,
            step_started,
            step_completed,
            error_code=None,
            error_message=None
        ):
            step_data = {

                "session_id":
                    session_id,

                "step_name":
                    step_name,

                "status":
                    status,

                "started_at":
                    step_started,

                "completed_at":
                    step_completed,

                "duration_ms":
                    int(
                        (
                            step_completed -
                            step_started
                        ).total_seconds() * 1000
                    )
            }

            if error_code is not None:
                step_data["error_code"] = str(
                    error_code
                )

            if error_message is not None:
                step_data["error_message"] = str(
                    error_message
                )

            session_steps.append(
                AuditSessionStep(
                    **step_data
                )
            )

        def build_and_print_summary():
            summary = build_session_summary(
                context=session_context,
                steps=session_steps
            )

            print(
                session_context.model_dump_json(
                    indent=2
                )
            )

            for step in session_steps:
                print(
                    step.model_dump_json(
                        indent=2
                    )
                )

            print(
                summary.model_dump_json(
                    indent=2
                )
            )

            return summary

        # =====================================================
        # RESOLVE : duplicate sam / display name / user dn
        # =====================================================

        actual_account = self.find_available_sam(
            LDAP_BASE_DN,
            request.sam_account_name
        )

        actual_display_name = self.find_available_display_name(
            LDAP_BASE_DN,
            request.full_name
        )

        request.sam_account_name = actual_account

        request.display_name = actual_display_name

        user_dn = self.build_user_dn(
            request.display_name,
            request.target_ou_dn
        )

        upn = (
            f"{actual_account}"
            "@automate.com.vn"
        )

        session_context.actual.account = actual_account

        session_context.actual.display_name = actual_display_name

        session_context.actual.user_dn = user_dn

        session_context.actual.ou_dn = request.target_ou_dn

        print(
            "FULL_NAME:",
            request.full_name
        )

        print(
            "DISPLAY_NAME:",
            request.display_name
        )

        # =====================================================
        # DRY RUN
        # =====================================================

        if request.dry_run:

            finalize_context(
                status="DRY_RUN"
            )

            summary = build_and_print_summary()

            return {

                "success":
                    True,

                "dry_run":
                    True,

                "session_id":
                    session_id,

                "capability":
                    "create_user",

                "requested_account":
                    requested_account,

                "actual_account":
                    actual_account,

                "DisplayName":
                    actual_display_name,

                "will_create_dn":
                    user_dn,

                "attributes": {

                    "displayName":
                        request.display_name,

                    "sAMAccountName":
                        actual_account,

                    "userPrincipalName":
                        upn,

                    "title":
                        request.title,

                    "department":
                        request.department,

                    "description":
                        request.description
                },

                "session_context":
                    session_context,

                "session_steps":
                    session_steps,

                "session_summary":
                    summary
            }

        attributes = {

            "cn":
                request.display_name,

            "displayName":
                request.display_name,

            "name":
                request.display_name,

            "givenName":
                request.first_name,

            "sn":
                request.last_name,

            "sAMAccountName":
                request.sam_account_name,

            "userPrincipalName":
                upn,

            "title":
                request.title,

            "department":
                request.department,

            "description":
                request.description
        }

        # =====================================================
        # STEP : add_user
        # =====================================================

        step_started = datetime.utcnow()

        result = self.connection.add(
            dn=user_dn,
            object_class=[
                "top",
                "person",
                "organizationalPerson",
                "user"
            ],
            attributes=attributes
        )

        print(
            "ADD USER:",
            self.connection.result
        )

        step_completed = datetime.utcnow()

        if not result:

            append_step(
                step_name="add_user",
                status="FAILED",
                step_started=step_started,
                step_completed=step_completed,
                error_code=self.connection.result.get(
                    "result"
                ),
                error_message=self.connection.result.get(
                    "description"
                )
            )

            finalize_context(
                status="FAILED",
                failure_stage="add_user",
                failure_code=self.connection.result.get(
                    "result"
                ),
                failure_reason=self.connection.result.get(
                    "description"
                )
            )

            summary = build_and_print_summary()
            save_step(session_steps[-1])
            return {

                "success":
                    False,

                "session_id":
                    session_id,

                "capability":
                    "create_user",

                "requested_account":
                    requested_account,

                "actual_account":
                    actual_account,

                "DisplayName":
                    actual_display_name,

                "error":
                    self.connection.result,

                "session_context":
                    session_context,

                "session_steps":
                    session_steps,

                "session_summary":
                    summary
            }

        append_step(
            step_name="add_user",
            status="SUCCESS",
            step_started=step_started,
            step_completed=step_completed
        )
        save_step(session_steps[-1])

        # =====================================================
        # STEP : set_password
        # =====================================================

        step_started = datetime.utcnow()

        password_result = self.set_password(
            user_dn,
            request.password
        )

        step_completed = datetime.utcnow()

        if not password_result:

            append_step(
                step_name="set_password",
                status="FAILED",
                step_started=step_started,
                step_completed=step_completed,
                error_code=self.connection.result.get(
                    "result"
                ),
                error_message=self.connection.result.get(
                    "description"
                )
            )

            finalize_context(
                status="FAILED",
                failure_stage="set_password",
                failure_code=self.connection.result.get(
                    "result"
                ),
                failure_reason=self.connection.result.get(
                    "description"
                )
            )

            summary = build_and_print_summary()
            save_step(session_steps[-1])
            return {

                "success":
                    False,

                "session_id":
                    session_id,

                "capability":
                    "create_user",

                "requested_account":
                    requested_account,

                "actual_account":
                    actual_account,

                "DisplayName":
                    actual_display_name,

                "error":
                    self.connection.result,

                "session_context":
                    session_context,

                "session_steps":
                    session_steps,

                "session_summary":
                    summary
            }

        append_step(
            step_name="set_password",
            status="SUCCESS",
            step_started=step_started,
            step_completed=step_completed
        )
        save_step(session_steps[-1])

        # =====================================================
        # STEP : enable_user
        # =====================================================

        step_started = datetime.utcnow()

        enable_result = self.enable_user(
            user_dn
        )

        step_completed = datetime.utcnow()

        if not enable_result:

            append_step(
                step_name="enable_user",
                status="FAILED",
                step_started=step_started,
                step_completed=step_completed,
                error_code=self.connection.result.get(
                    "result"
                ),
                error_message=self.connection.result.get(
                    "description"
                )
            )

            finalize_context(
                status="FAILED",
                failure_stage="enable_user",
                failure_code=self.connection.result.get(
                    "result"
                ),
                failure_reason=self.connection.result.get(
                    "description"
                )
            )

            summary = build_and_print_summary()
            save_step(session_steps[-1])
            return {

                "success":
                    False,

                "session_id":
                    session_id,

                "capability":
                    "create_user",

                "requested_account":
                    requested_account,

                "actual_account":
                    actual_account,

                "DisplayName":
                    actual_display_name,

                "error":
                    self.connection.result,

                "session_context":
                    session_context,

                "session_steps":
                    session_steps,

                "session_summary":
                    summary
            }

        append_step(
            step_name="enable_user",
            status="SUCCESS",
            step_started=step_started,
            step_completed=step_completed
        )
        save_step(session_steps[-1])

        # =====================================================
        # STEP : force_change_password
        # =====================================================

        step_started = datetime.utcnow()

        force_result = self.force_change_password_next_logon(
            user_dn
        )

        step_completed = datetime.utcnow()

        if not force_result:

            append_step(
                step_name="force_change_password",
                status="FAILED",
                step_started=step_started,
                step_completed=step_completed,
                error_code=self.connection.result.get(
                    "result"
                ),
                error_message=self.connection.result.get(
                    "description"
                )
            )

            finalize_context(
                status="FAILED",
                failure_stage="force_change_password",
                failure_code=self.connection.result.get(
                    "result"
                ),
                failure_reason=self.connection.result.get(
                    "description"
                )
            )

            summary = build_and_print_summary()
            save_step(session_steps[-1])
            return {

                "success":
                    False,

                "session_id":
                    session_id,

                "capability":
                    "create_user",

                "requested_account":
                    requested_account,

                "actual_account":
                    actual_account,

                "DisplayName":
                    actual_display_name,

                "error":
                    self.connection.result,

                "session_context":
                    session_context,

                "session_steps":
                    session_steps,

                "session_summary":
                    summary
            }

        append_step(
            step_name="force_change_password",
            status="SUCCESS",
            step_started=step_started,
            step_completed=step_completed
        )
        save_step(session_steps[-1])

        # =====================================================
        # STEP : Add user to groups
        # =====================================================
        step_started = datetime.utcnow()

        group_result = self.add_user_to_groups(
            user_dn=user_dn,
            groups=request.groups
        )

        step_completed = datetime.utcnow()

        if not group_result["success"]:

            session_steps.append(

                AuditSessionStep(

                    session_id=session_id,

                    step_name="add_groups",

                    status="FAILED",

                    started_at=step_started,

                    completed_at=step_completed,

                    duration_ms=int(
                        (
                            step_completed -
                            step_started
                        ).total_seconds() * 1000
                    ),

                    details={

                        "added_groups":
                            group_result[
                                "added_groups"
                            ],

                        "failed_groups":
                            group_result[
                                "failed_groups"
                            ]
                    }
                )
            )

            finalize_context(
                status="FAILED",
                failure_stage="add_groups",
                failure_reason=
                    "Failed add groups"
            )

            summary = build_and_print_summary()
            save_step(session_steps[-1])
            return {
                "success": False,

                "session_id":
                    session_id,

                "session_context":
                    session_context,

                "session_steps":
                    session_steps,

                "session_summary":
                    summary
            }
    
        session_steps.append(

            AuditSessionStep(

                session_id=session_id,

                step_name="add_groups",

                status="SUCCESS",

                started_at=step_started,

                completed_at=step_completed,

                duration_ms=int(
                    (
                        step_completed -
                        step_started
                    ).total_seconds() * 1000
                ),

                details={

                    "added_groups":
                        group_result[
                            "added_groups"
                        ]
                }
            )
        )
        save_step(session_steps[-1])



        # =====================================================
        # SESSION SUCCESS
        # =====================================================

        finalize_context(
            status="SUCCESS"
        )

        summary = build_and_print_summary()
        save_summary(summary)
        return {

            "success":
                True,

            "session_id":
                session_id,

            "capability":
                "create_user",

            "requested_account":
                requested_account,

            "actual_account":
                actual_account,

            "DisplayName":
                actual_display_name,

            "title":
                request.title,

            "department":
                request.department,

            "status":
                "completed",

            "session_context":
                session_context,

            "session_steps":
                session_steps,

            "session_summary":
                summary
        }
    


    def build_user_dn(
        self,
        full_name,
        target_ou_dn
    ):

        return (
            f"CN={full_name},"
            f"{target_ou_dn}"
        )
    
    
    def find_available_sam(
        self,
        base_dn,
        base_account
    ):

        base_account = base_account.lower()

        self.connection.search(
            search_base=base_dn,
            search_filter=f"(sAMAccountName={base_account}*)",
            attributes=["sAMAccountName"]
        )

        accounts = []

        for entry in self.connection.entries:

            accounts.append(
                str(
                    entry.sAMAccountName
                ).lower()
            )

        # chưa tồn tại
        if base_account not in accounts:

            return base_account

        max_suffix = 0

        for account in accounts:

            # sonnm
            if account == base_account:
                continue

            m = re.match(
                rf"^{re.escape(base_account)}(\d+)$",
                account
            )

            if m:

                max_suffix = max(
                    max_suffix,
                    int(m.group(1))
                )

        return f"{base_account}{max_suffix + 1}"


    def find_available_display_name(
        self,
        base_dn: str,
        base_display_name: str
    ) -> str:

        self.connection.search(
            search_base=base_dn,
            search_filter=f"(displayName={base_display_name}*)",
            attributes=["displayName"]
        )

        display_names = []

        for entry in self.connection.entries:

            try:
                display_names.append(
                    str(entry["displayName"].value)
                )
            except Exception:
                pass

        # Chưa tồn tại
        if base_display_name not in display_names:
            return base_display_name

        max_suffix = 0

        pattern = re.compile(
            rf"^{re.escape(base_display_name)} (\d+)$"
        )

        for name in display_names:

            match = pattern.match(name)

            if match:

                max_suffix = max(
                    max_suffix,
                    int(match.group(1))
                )

        return f"{base_display_name} {max_suffix + 1}"


    def set_password(
        self,
        user_dn,
        password
    ):

        result = ad_modify_password(
            self.connection,
            user_dn,
            password,
            None
        )

        print(
            "SET PASSWORD:",
            self.connection.result
        )

        return result
    
    def enable_user(
        self,
        user_dn
    ):

        result = self.connection.modify(
            user_dn,
            {
                "userAccountControl": [
                    (
                        MODIFY_REPLACE,
                        [512]
                    )
                ]
            }
        )

        print(
            "ENABLE USER:",
            self.connection.result
        )

        return result
    

    def force_change_password_next_logon(
        self,
        user_dn
    ):

        result = self.connection.modify(
            user_dn,
            {
                "pwdLastSet": [
                    (
                        MODIFY_REPLACE,
                        [0]
                    )
                ]
            }
        )

        print(
            "FORCE PASSWORD CHANGE:",
            self.connection.result
        )

        return result
    

    def add_user_to_groups(
        self,
        user_dn: str,
        groups: list[str]
    ):
        added_groups = []

        failed_groups = []

        for group_dn in groups:

            result = self.connection.modify(
                group_dn,
                {
                    "member": [
                        (
                            MODIFY_ADD,
                            [user_dn]
                        )
                    ]
                }
            )

            if result:
                added_groups.append(
                    group_dn
                )
            else:
                failed_groups.append(
                    group_dn
                )

        return {
            "success":
                len(failed_groups) == 0,

            "added_groups":
                added_groups,

            "failed_groups":
                failed_groups
        }