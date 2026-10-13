from ldap3 import Server, Tls
from ldap3 import Connection
from ldap3 import ALL
from ldap3 import MODIFY_REPLACE, MODIFY_ADD, MODIFY_DELETE
from ldap3.extend.microsoft.modifyPassword import ad_modify_password
import re
import ssl
from app.audit.onboarding_audit import OnboardingAudit
from datetime import datetime
from ldap3.utils.conv import escape_filter_chars

from app.config import *

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
        print("=" * 80)
        print("LDAP CONNECT")
        print("HOST     =", host)
        print("USER     =", username)
        print("PORT     =", port)
        print("=" * 80)
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
        audit: OnboardingAudit | None = None,
    ):
        requested_account = request.sam_account_name
        request.display_name = request.display_name or request.full_name
        if audit is None:
            audit = OnboardingAudit(
                source_request_id=request.source_request_id,
                employee_id=request.employee_id,
                requested_account=requested_account,
            )
        actual_account = None
        actual_display_name = None

        def run_step(step_name, operation, details=None):
            step_started = datetime.utcnow()
            try:
                result = operation()
            except Exception as ex:
                audit.record_step(
                    step_name=step_name,
                    success=False,
                    started_at=step_started,
                    completed_at=datetime.utcnow(),
                    details={"error_type": type(ex).__name__},
                )
                raise

            if isinstance(result, dict) and "success" in result:
                succeeded = bool(result["success"])
            else:
                succeeded = bool(result)

            audit.record_step(
                step_name=step_name,
                success=succeeded,
                started_at=step_started,
                completed_at=datetime.utcnow(),
                details=details(result) if callable(details) else details,
            )
            return result

        def failure_result(step_name, error=None):
            audit.set_actual_account(actual_account)
            audit.finish("FAILED")
            return {
                "success": False,
                "source_request_id": request.source_request_id,
                "capability": "create_user",
                "failed_step": step_name,
                "requested_account": requested_account,
                "actual_account": actual_account,
                "DisplayName": actual_display_name,
                "error": error if error is not None else self.connection.result,
            }

        try:
            actual_account = run_step(
                "resolve_sam_account_name",
                lambda: self.find_available_sam(
                    LDAP_BASE_DN,
                    request.sam_account_name,
                ),
            )
            if not actual_account:
                return failure_result("resolve_sam_account_name")

            actual_display_name = run_step(
                "resolve_display_name",
                lambda: self.find_available_display_name(
                    LDAP_BASE_DN,
                    request.display_name,
                ),
            )
            if not actual_display_name:
                return failure_result("resolve_display_name")

            request.sam_account_name = actual_account
            request.display_name = actual_display_name
            user_dn = self.build_user_dn(
                actual_display_name,
                request.target_ou_dn,
            )
            upn = f"{actual_account}@automate.com.vn"

            if request.dry_run:
                audit.set_actual_account(actual_account)
                audit.finish("DRY_RUN")
                return {
                    "success": True,
                    "dry_run": True,
                    "source_request_id": request.source_request_id,
                    "capability": "create_user",
                    "requested_account": requested_account,
                    "actual_account": actual_account,
                    "DisplayName": actual_display_name,
                    "will_create_dn": user_dn,
                    "attributes": {
                        "displayName": actual_display_name,
                        "sAMAccountName": actual_account,
                        "userPrincipalName": upn,
                        "title": request.title,
                        "department": request.department,
                        "description": request.description,
                    },
                }

            attributes = {
                "cn": actual_display_name,
                "displayName": actual_display_name,
                "name": actual_display_name,
                "givenName": request.first_name,
                "sn": request.last_name,
                "sAMAccountName": actual_account,
                "userPrincipalName": upn,
                "title": request.title,
                "department": request.department,
            }
            if request.description:
                attributes["description"] = request.description

            add_result = run_step(
                "add_user",
                lambda: self.connection.add(
                    dn=user_dn,
                    object_class=[
                        "top",
                        "person",
                        "organizationalPerson",
                        "user",
                    ],
                    attributes=attributes,
                ),
            )
            if not add_result:
                return failure_result("add_user")

            password_result = run_step(
                "set_password",
                lambda: self.set_password(user_dn, request.password),
            )
            if not password_result:
                return failure_result("set_password")

            enable_result = run_step(
                "enable_user",
                lambda: self._enable_user_by_dn(user_dn),
            )
            if not enable_result:
                return failure_result("enable_user")

            force_result = run_step(
                "force_change_password",
                lambda: self.force_change_password_next_logon(user_dn),
            )
            if not force_result:
                return failure_result("force_change_password")

            group_result = run_step(
                "add_groups",
                lambda: self.add_user_to_groups(
                    user_dn=user_dn,
                    groups=request.groups,
                ),
                details=lambda result: {
                    "added_groups": result.get("added_groups", []),
                    "failed_groups": result.get("failed_groups", []),
                },
            )
            if not group_result["success"]:
                return failure_result("add_groups", group_result)

            audit.set_actual_account(actual_account)
            audit.finish("SUCCESS")
            return {
                "success": True,
                "source_request_id": request.source_request_id,
                "capability": "create_user",
                "requested_account": requested_account,
                "actual_account": actual_account,
                "DisplayName": actual_display_name,
                "title": request.title,
                "department": request.department,
                "status": "completed",
            }
        except Exception:
            audit.set_actual_account(actual_account)
            audit.finish("FAILED")
            raise


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

        escaped_display_name = (
            escape_filter_chars(
                base_display_name
            )
        )

        self.connection.search(
            search_base=base_dn,

            search_filter=(
                f"(displayName="
                f"{escaped_display_name}*)"
            ),

            attributes=[
                "displayName"
            ]
        )

        display_names = []

        for entry in self.connection.entries:

            try:

                display_names.append(
                    str(
                        entry["displayName"].value
                    )
                )

            except Exception:
                pass

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

        return (
            f"{base_display_name} "
            f"{max_suffix + 1}"
        )



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
    
    def _enable_user_by_dn(
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
    
    def get_group_dn(
        self,
        group_name: str
    ):
        print("\n" + "=" * 80)
        print("GET GROUP DN")
        print("GROUP NAME =", repr(group_name))
        print("LDAP_BASE_DN =", LDAP_BASE_DN)

        search_filter = (
            f"(cn={group_name})"
        )

        print("SEARCH FILTER =", repr(search_filter))
        print("=" * 80)

        try:

            self.connection.search(
                search_base=LDAP_BASE_DN,
                search_filter=search_filter,
                attributes=[
                    "distinguishedName",
                    "cn"
                ]
            )

            print(
                "SEARCH RESULT COUNT =",
                len(self.connection.entries)
            )

            for entry in self.connection.entries:
                print(
                    "FOUND ENTRY =",
                    entry.entry_dn
                )

            if not self.connection.entries:

                print(
                    "[GROUP NOT FOUND]"
                )

                return None

            entry = self.connection.entries[0]

            group_dn = str(
                entry.entry_dn
            )

            print(
                "GROUP DN =",
                group_dn
            )

            return group_dn

        except Exception as ex:

            print(
                "[GET GROUP DN ERROR]"
            )

            print(type(ex))
            print(str(ex))

            raise

    def add_user_to_groups(
        self,
        user_dn: str,
        groups: list[str]
    ):
        added_groups = []

        failed_groups = []

        print("\n" + "=" * 80)
        print("ADD USER TO GROUPS")
        print("USER DN =", user_dn)
        print("GROUPS =", groups)
        print("=" * 80)

        for group_name in groups:

            try:

                group_dn = self.get_group_dn(
                    group_name
                )

                if not group_dn:

                    failed_groups.append(
                        group_name
                    )

                    continue

                print("\n" + "=" * 80)
                print("ADDING MEMBER")
                print("GROUP DN =", group_dn)
                print("USER DN =", user_dn)
                print("=" * 80)

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

                print(
                    "LDAP RESULT =",
                    self.connection.result
                )

                if result:

                    added_groups.append(
                        group_name
                    )

                else:

                    failed_groups.append(
                        group_name
                    )

            except Exception as ex:

                print(
                    "[GROUP ERROR]"
                )

                print(ex)

                failed_groups.append(
                    group_name
                )

        return {

            "success":
                len(failed_groups) == 0,

            "added_groups":
                added_groups,

            "failed_groups":
                failed_groups
        }
    
    #================================
    # AD TOOL - Disable User
    #================================
    def disable_user(
        self,
        sam_account_name: str
    ):

        search_filter = (
            f"(sAMAccountName={sam_account_name})"
        )

        self.connection.search(
            search_base=LDAP_BASE_DN,
            search_filter=search_filter,
            attributes=[
                "distinguishedName",
                "userAccountControl"
            ]
        )

        if not self.connection.entries:
            raise Exception(
                f"User not found: {sam_account_name}"
            )

        user = self.connection.entries[0]

        user_dn = str(
            user.distinguishedName.value
        )

        current_uac = int(
            user.userAccountControl.value
        )

        ACCOUNTDISABLE = 2

        new_uac = (
            current_uac | ACCOUNTDISABLE
        )

        success = self.connection.modify(
            user_dn,
            {
                "userAccountControl": [
                    (
                        MODIFY_REPLACE,
                        [new_uac]
                    )
                ]
            }
        )

        if not success:
            raise Exception(
                self.connection.result
            )

        return {
            "success": True,
            "action": "disable_user",
            "sam_account_name": sam_account_name,
            "user_dn": user_dn
        }

    #================================
    # AD TOOL - Enable User
    #================================
    def enable_user(
        self,
        sam_account_name: str
    ):

        search_filter = (
            f"(sAMAccountName={sam_account_name})"
        )

        self.connection.search(
            search_base=LDAP_BASE_DN,
            search_filter=search_filter,
            attributes=[
                "distinguishedName",
                "userAccountControl"
            ]
        )

        if not self.connection.entries:
            raise Exception(
                f"User not found: {sam_account_name}"
            )

        user = self.connection.entries[0]

        user_dn = str(
            user.distinguishedName.value
        )

        current_uac = int(
            user.userAccountControl.value
        )

        ACCOUNTDISABLE = 2

        new_uac = (
            current_uac & ~ACCOUNTDISABLE
        )

        success = self.connection.modify(
            user_dn,
            {
                "userAccountControl": [
                    (
                        MODIFY_REPLACE,
                        [new_uac]
                    )
                ]
            }
        )

        if not success:
            raise Exception(
                self.connection.result
            )

        return {
            "success": True,
            "action": "enable_user",
            "sam_account_name": sam_account_name,
            "user_dn": user_dn
        }

    def get_user_status(
        self,
        sam_account_name: str
    ):
        self.connection.search(
            search_base=LDAP_BASE_DN,
            search_filter=(
                f"(sAMAccountName={sam_account_name})"
            ),
            attributes=[
                "userAccountControl"
            ]
        )

        if not self.connection.entries:
            raise Exception(
                f"User not found: {sam_account_name}"
            )

        current_uac = int(
            self.connection.entries[0]
            .userAccountControl.value
        )

        return (
            "disabled"
            if current_uac & 2
            else "enabled"
        )

    #===================================
    # AD TOOL - UPDATE USER DISPLAYNAME
    #===================================
    def update_user_displayname(
        self,
        sam_account_name: str,
        new_display_name: str
    ):

        search_filter = (
            f"(sAMAccountName={sam_account_name})"
        )

        self.connection.search(
            search_base=LDAP_BASE_DN,
            search_filter=search_filter,
            attributes=[
                "distinguishedName",
                "displayName"
            ]
        )

        if not self.connection.entries:
            raise Exception(
                f"User not found: {sam_account_name}"
            )

        user = self.connection.entries[0]

        user_dn = str(
            user.distinguishedName.value
        )

        success = self.connection.modify(
            user_dn,
            {
                "displayName": [
                    (
                        MODIFY_REPLACE,
                        [new_display_name]
                    )
                ]
            }
        )

        if not success:
            raise Exception(
                self.connection.result
            )

        return {
            "success": True,
            "action":
                "update_user_displayName",

            "sam_account_name":
                sam_account_name,

            "new_display_name":
                new_display_name,

            "user_dn":
                user_dn
        }
    
    #===================================
    # AD TOOL - UPDATE USER IP PHONE
    #===================================
    def update_user_ip_phone(
        self,
        sam_account_name: str,
        new_ip_phone: str
    ):

        search_filter = (
            f"(sAMAccountName={sam_account_name})"
        )

        self.connection.search(
            search_base=LDAP_BASE_DN,
            search_filter=search_filter,
            attributes=[
                "distinguishedName",
                "ipPhone"
            ]
        )

        if not self.connection.entries:
            raise Exception(
                f"User not found: {sam_account_name}"
            )

        user = self.connection.entries[0]

        user_dn = str(
            user.distinguishedName.value
        )

        success = self.connection.modify(
            user_dn,
            {
                "ipPhone": [
                    (
                        MODIFY_REPLACE,
                        [new_ip_phone]
                    )
                ]
            }
        )

        if not success:
            raise Exception(
                self.connection.result
            )

        return {
            "success": True,
            "action":
                "update_user_ip_phone",

            "sam_account_name":
                sam_account_name,

            "new_ip_phone":
                new_ip_phone,

            "user_dn":
                user_dn
        }

    #==================================
    # AD TOOL - UPDATE USER DEPARTMENT
    #==================================
    def update_user_department(
        self,
        sam_account_name: str,
        new_value: str
    ):

        search_filter = (
            f"(sAMAccountName={sam_account_name})"
        )

        self.connection.search(
            search_base=LDAP_BASE_DN,
            search_filter=search_filter,
            attributes=[
                "distinguishedName",
                "displayName"
            ]
        )

        if not self.connection.entries:
            raise Exception(
                f"User not found: {sam_account_name}"
            )

        user = self.connection.entries[0]

        user_dn = str(
            user.distinguishedName.value
        )

        success = self.connection.modify(
            user_dn,
            {
                "department": [
                    (
                        MODIFY_REPLACE,
                        [new_value]
                    )
                ]
            }
        )

        if not success:
            raise Exception(
                self.connection.result
            )

        return {
            "success": True,
            "action":
                "update_user_department",

            "sam_account_name":
                sam_account_name,

            "new_value":
                new_value,

            "user_dn":
                user_dn
        }

    #==================================
    # AD TOOL - UPDATE USER DESCRIPTON
    #==================================
    def update_user_description(
        self,
        sam_account_name: str,
        new_value: str
    ):

        search_filter = (
            f"(sAMAccountName={sam_account_name})"
        )

        self.connection.search(
            search_base=LDAP_BASE_DN,
            search_filter=search_filter,
            attributes=[
                "distinguishedName",
                "displayName"
            ]
        )

        if not self.connection.entries:
            raise Exception(
                f"User not found: {sam_account_name}"
            )

        user = self.connection.entries[0]

        user_dn = str(
            user.distinguishedName.value
        )

        success = self.connection.modify(
            user_dn,
            {
                "description": [
                    (
                        MODIFY_REPLACE,
                        [new_value]
                    )
                ]
            }
        )

        if not success:
            raise Exception(
                self.connection.result
            )

        return {
            "success": True,
            "action":
                "update_user_description",

            "sam_account_name":
                sam_account_name,

            "new_value":
                new_value,

            "user_dn":
                user_dn
        }


    #================================
    # AD TOOL - ADD GROUP MEMBER 
    #================================
    def add_group_member(
        self,
        sam_account_name: str,
        group_name: str
    ):

        # tìm user

        self.connection.search(
            search_base=LDAP_BASE_DN,
            search_filter=(
                f"(sAMAccountName={sam_account_name})"
            ),
            attributes=[
                "distinguishedName"
            ]
        )

        if not self.connection.entries:
            raise Exception(
                f"User not found: {sam_account_name}"
            )

        user_dn = str(
            self.connection.entries[0]
            .distinguishedName.value
        )

        # tìm group

        self.connection.search(
            search_base=LDAP_BASE_DN,
            search_filter=(
                f"(cn={group_name})"
            ),
            attributes=[
                "distinguishedName"
            ]
        )

        if not self.connection.entries:
            raise Exception(
                f"Group not found: {group_name}"
            )

        group_dn = str(
            self.connection.entries[0]
            .distinguishedName.value
        )

        success = self.connection.modify(
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

        if not success:
            raise Exception(
                self.connection.result
            )

        return {
            "success": True,
            "action": "add_group_member",
            "user": sam_account_name,
            "group": group_name
        }
    #================================
    # AD TOOL - ADD GROUP MEMBER BY DN
    #================================

    def add_group_member_by_dn(
        self,
        sam_account_name: str,
        group_dn: str,
    ):
        
        self.connection.search(
            search_base=
                LDAP_BASE_DN,

            search_filter=(
                f"(sAMAccountName="
                f"{sam_account_name})"
            ),

            attributes=[
                "distinguishedName"
            ]
        )

        if not self.connection.entries:
            raise Exception(
                f"User not found: "
                f"{sam_account_name}"
            )

        user_dn = str(
            self.connection
            .entries[0]
            .distinguishedName
            .value
        )

        success = (
            self.connection.modify(
                group_dn,
                {
                    "member": [
                        (
                            MODIFY_ADD,
                            [
                                user_dn
                            ]
                        )
                    ]
                }
            )
        )

        if not success:
            raise Exception(
                self.connection.result
            )

        return {
            "success": True,

            "action":
                "add_group_member_by_dn",

            "sam_account_name":
                sam_account_name,

            "user_dn":
                user_dn,

            "group_dn":
                group_dn,
        }

    #================================
    # AD TOOL - REMOVE GROUP MEMBER #
    #================================
    def remove_group_member(
        self,
        sam_account_name: str,
        group_name: str
    ):

        self.connection.search(
            search_base=LDAP_BASE_DN,
            search_filter=(
                f"(sAMAccountName={sam_account_name})"
            ),
            attributes=[
                "distinguishedName"
            ]
        )

        if not self.connection.entries:
            raise Exception(
                f"User not found: {sam_account_name}"
            )

        user_dn = str(
            self.connection.entries[0]
            .distinguishedName.value
        )

        self.connection.search(
            search_base=LDAP_BASE_DN,
            search_filter=(
                f"(cn={group_name})"
            ),
            attributes=[
                "distinguishedName"
            ]
        )

        if not self.connection.entries:
            raise Exception(
                f"Group not found: {group_name}"
            )

        group_dn = str(
            self.connection.entries[0]
            .distinguishedName.value
        )

        success = self.connection.modify(
            group_dn,
            {
                "member": [
                    (
                        MODIFY_DELETE,
                        [user_dn]
                    )
                ]
            }
        )

        if not success:
            raise Exception(
                self.connection.result
            )

        return {
            "success": True,
            "action": "remove_group_member",
            "user": sam_account_name,
            "group": group_name
        }

    # ==========================================
    # REMOVE USER FROM GROUP BY DN
    # ==========================================
    def remove_group_member_by_dn(
        self,
        sam_account_name: str,
        group_dn: str,
    ):
    
        self.connection.search(
            search_base=
                LDAP_BASE_DN,

            search_filter=(
                f"(sAMAccountName="
                f"{sam_account_name})"
            ),

            attributes=[
                "distinguishedName"
            ]
        )

        if not self.connection.entries:
            raise Exception(
                f"User not found: "
                f"{sam_account_name}"
            )

        user_dn = str(
            self.connection
            .entries[0]
            .distinguishedName
            .value
        )

        success = (
            self.connection.modify(
                group_dn,
                {
                    "member": [
                        (
                            MODIFY_DELETE,
                            [
                                user_dn
                            ]
                        )
                    ]
                }
            )
        )

        if not success:
            raise Exception(
                self.connection.result
            )

        return {
            "success": True,

            "action":
                "remove_group_member_by_dn",

            "sam_account_name":
                sam_account_name,

            "user_dn":
                user_dn,

            "group_dn":
                group_dn,
        }

    #================================
    # AD TOOL - MOVE USER TO OU #
    #================================
    def move_user_to_ou(
        self,
        sam_account_name: str,
        target_ou_dn: str
    ):

        self.connection.search(
            search_base=LDAP_BASE_DN,
            search_filter=(
                f"(sAMAccountName={sam_account_name})"
            ),
            attributes=[
                "distinguishedName"
            ]
        )

        if not self.connection.entries:
            raise Exception(
                f"User not found: {sam_account_name}"
            )

        old_dn = str(
            self.connection.entries[0]
            .distinguishedName.value
        )

        rdn = old_dn.split(",")[0]

        success = self.connection.modify_dn(
            old_dn,
            relative_dn=rdn,
            new_superior=target_ou_dn
        )

        if not success:
            raise Exception(
                self.connection.result
            )

        return {
            "success": True,
            "action": "move_user_to_ou",
            "user": sam_account_name,
            "target_ou": target_ou_dn
        }
    #================================
    # AD TOOL - DISABLE COMPUTER #
    #================================
    def disable_computer(
        self,
        computer_name: str
    ):

        search_filter = (
            f"(sAMAccountName={computer_name}$)"
        )

        self.connection.search(
            search_base=LDAP_BASE_DN,
            search_filter=search_filter,
            attributes=[
                "distinguishedName",
                "userAccountControl"
            ]
        )

        if not self.connection.entries:
            raise Exception(
                f"Computer not found: {computer_name}"
            )

        computer = self.connection.entries[0]

        computer_dn = str(
            computer.distinguishedName.value
        )

        current_uac = int(
            computer.userAccountControl.value
        )

        ACCOUNTDISABLE = 2

        new_uac = (
            current_uac | ACCOUNTDISABLE
        )

        success = self.connection.modify(
            computer_dn,
            {
                "userAccountControl": [
                    (
                        MODIFY_REPLACE,
                        [new_uac]
                    )
                ]
            }
        )

        if not success:
            raise Exception(
                self.connection.result
            )

        return {
            "success": True,
            "action": "disable_computer",
            "computer_name": computer_name,
            "computer_dn": computer_dn
        }

    #================================
    # AD TOOL - CREATE GROUP
    #================================
    def create_group(
            self,
            group_name: str,
            target_ou_dn: str,
            description: str | None = None
        ):
    
            group_dn = (
                f"CN={group_name},"
                f"{target_ou_dn}"
            )
    
            attributes = {
                "cn": group_name,
                "name": group_name,
                "sAMAccountName": group_name,
                "groupType": -2147483646
            }
    
            if description is not None:
                attributes["description"] = description
    
            success = self.connection.add(
                dn=group_dn,
                object_class=[
                    "top",
                    "group"
                ],
                attributes=attributes
            )
    
            if not success:
                raise Exception(
                    self.connection.result
                )
    
            return {
                "success": True,
                "action": "create_group",
                "group_name": group_name,
                "group_dn": group_dn
            }


    #================================
    # AD TOOL - MOVE GROUP TO OU
    #================================
    def move_group_to_ou(
        self,
        group_name: str,
        target_ou_dn: str
    ):

        self.connection.search(
            search_base=LDAP_BASE_DN,
            search_filter=(
                f"(cn={group_name})"
            ),
            attributes=[
                "distinguishedName"
            ]
        )

        if not self.connection.entries:
            raise Exception(
                f"Group not found: {group_name}"
            )

        old_dn = str(
            self.connection.entries[0]
            .distinguishedName.value
        )

        rdn = old_dn.split(",")[0]

        success = self.connection.modify_dn(
            old_dn,
            relative_dn=rdn,
            new_superior=target_ou_dn
        )

        if not success:
            raise Exception(
                self.connection.result
            )

        group_dn = (
            f"{rdn},"
            f"{target_ou_dn}"
        )

        return {
            "success": True,
            "action": "move_group_to_ou",
            "group": group_name,
            "group_dn": group_dn,
            "target_ou": target_ou_dn
        }


    #================================
    # AD TOOL - ADD COMPUTER TO GROUP
    #================================
    def add_computer_to_group(
        self,
        computer_name: str,
        group_name: str
    ):

        computer_sam_account_name = (
            computer_name
            if computer_name.endswith("$")
            else f"{computer_name}$"
        )

        self.connection.search(
            search_base=LDAP_BASE_DN,
            search_filter=(
                f"(sAMAccountName={computer_sam_account_name})"
            ),
            attributes=[
                "distinguishedName"
            ]
        )

        if not self.connection.entries:
            raise Exception(
                f"Computer not found: {computer_name}"
            )

        computer_dn = str(
            self.connection.entries[0]
            .distinguishedName.value
        )

        self.connection.search(
            search_base=LDAP_BASE_DN,
            search_filter=(
                f"(cn={group_name})"
            ),
            attributes=[
                "distinguishedName"
            ]
        )

        if not self.connection.entries:
            raise Exception(
                f"Group not found: {group_name}"
            )

        group_dn = str(
            self.connection.entries[0]
            .distinguishedName.value
        )

        success = self.connection.modify(
            group_dn,
            {
                "member": [
                    (
                        MODIFY_ADD,
                        [computer_dn]
                    )
                ]
            }
        )

        if not success:
            raise Exception(
                self.connection.result
            )

        return {
            "success": True,
            "action": "move_computer_to_group",
            "computer": computer_name,
            "computer_dn": computer_dn,
            "group": group_name,
            "group_dn": group_dn
        }

    #================================
    # AD TOOL - MOVE COMPUTER TO OU
    #================================
    def move_computer_to_ou(
        self,
        computer_name: str,
        target_ou_dn: str
    ):

        computer_sam_account_name = (
            computer_name
            if computer_name.endswith("$")
            else f"{computer_name}$"
        )

        self.connection.search(
            search_base=LDAP_BASE_DN,
            search_filter=(
                f"(sAMAccountName={computer_sam_account_name})"
            ),
            attributes=[
                "distinguishedName"
            ]
        )

        if not self.connection.entries:
            raise Exception(
                f"Computer not found: {computer_name}"
            )

        old_dn = str(
            self.connection.entries[0]
            .distinguishedName.value
        )

        rdn = old_dn.split(",")[0]

        success = self.connection.modify_dn(
            old_dn,
            relative_dn=rdn,
            new_superior=target_ou_dn
        )

        if not success:
            raise Exception(
                self.connection.result
            )

        computer_dn = (
            f"{rdn},"
            f"{target_ou_dn}"
        )

        return {
            "success": True,
            "action": "move_computer_to_ou",
            "computer_name": computer_name,
            "computer_dn": computer_dn,
            "target_ou": target_ou_dn
        }


        