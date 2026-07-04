from ldap3 import Server, Tls
from ldap3 import Connection
from ldap3 import ALL
from ldap3 import MODIFY_REPLACE
from ldap3.extend.microsoft.modifyPassword import ad_modify_password
import re
import ssl
from app.models.session_step import AuditSessionStep
from datetime import datetime


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
    
    from datetime import datetime

    def create_user(
        self,
        request,
        session_id
    ):

        session_steps = []

        displayname = request.display_name

        user_dn = (
            f"CN={displayname},"
            f"{request.target_ou_dn}"
        )

        attributes = {

            "cn": displayname,

            "displayName": displayname,

            "name": displayname,

            "givenName": request.first_name,

            "sn": request.last_name,

            "sAMAccountName":
                request.sam_account_name,

            "userPrincipalName":
                f"{request.sam_account_name}@automate.com.vn",

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

            session_steps.append(

                AuditSessionStep(

                    session_id=session_id,

                    step_name="add_user",

                    status="FAILED",

                    started_at=step_started,

                    completed_at=step_completed,

                    duration_ms=int(
                        (
                            step_completed -
                            step_started
                        ).total_seconds() * 1000
                    ),

                    error_code=str(
                        self.connection.result.get(
                            "result"
                        )
                    ),

                    error_message=str(
                        self.connection.result.get(
                            "description"
                        )
                    )
                )
            )

            return {

                "success": False,

                "session_steps":
                    session_steps
            }

        session_steps.append(

            AuditSessionStep(

                session_id=session_id,

                step_name="add_user",

                status="SUCCESS",

                started_at=step_started,

                completed_at=step_completed,

                duration_ms=int(
                    (
                        step_completed -
                        step_started
                    ).total_seconds() * 1000
                )
            )
        )

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

            session_steps.append(

                AuditSessionStep(

                    session_id=session_id,

                    step_name="set_password",

                    status="FAILED",

                    started_at=step_started,

                    completed_at=step_completed,

                    duration_ms=int(
                        (
                            step_completed -
                            step_started
                        ).total_seconds() * 1000
                    )
                )
            )

            return {

                "success": False,

                "session_steps":
                    session_steps
            }

        session_steps.append(

            AuditSessionStep(

                session_id=session_id,

                step_name="set_password",

                status="SUCCESS",

                started_at=step_started,

                completed_at=step_completed,

                duration_ms=int(
                    (
                        step_completed -
                        step_started
                    ).total_seconds() * 1000
                )
            )
        )

        # =====================================================
        # STEP : enable_user
        # =====================================================

        step_started = datetime.utcnow()

        enable_result = self.enable_user(
            user_dn
        )

        step_completed = datetime.utcnow()

        if not enable_result:

            session_steps.append(

                AuditSessionStep(

                    session_id=session_id,

                    step_name="enable_user",

                    status="FAILED",

                    started_at=step_started,

                    completed_at=step_completed,

                    duration_ms=int(
                        (
                            step_completed -
                            step_started
                        ).total_seconds() * 1000
                    )
                )
            )

            return {

                "success": False,

                "session_steps":
                    session_steps
            }

        session_steps.append(

            AuditSessionStep(

                session_id=session_id,

                step_name="enable_user",

                status="SUCCESS",

                started_at=step_started,

                completed_at=step_completed,

                duration_ms=int(
                    (
                        step_completed -
                        step_started
                    ).total_seconds() * 1000
                )
            )
        )

        # =====================================================
        # STEP : force_change_password
        # =====================================================

        step_started = datetime.utcnow()

        force_result = (
            self.force_change_password_next_logon(
                user_dn
            )
        )

        step_completed = datetime.utcnow()

        if not force_result:

            session_steps.append(

                AuditSessionStep(

                    session_id=session_id,

                    step_name="force_change_password",

                    status="FAILED",

                    started_at=step_started,

                    completed_at=step_completed,

                    duration_ms=int(
                        (
                            step_completed -
                            step_started
                        ).total_seconds() * 1000
                    )
                )
            )

            return {

                "success": False,

                "session_steps":
                    session_steps
            }

        session_steps.append(

            AuditSessionStep(

                session_id=session_id,

                step_name="force_change_password",

                status="SUCCESS",

                started_at=step_started,

                completed_at=step_completed,

                duration_ms=int(
                    (
                        step_completed -
                        step_started
                    ).total_seconds() * 1000
                )
            )
        )

        return {

            "success": True,

            "session_steps":
                session_steps
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
    
    from ldap3 import MODIFY_REPLACE


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