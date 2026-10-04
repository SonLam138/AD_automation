import unittest
from types import SimpleNamespace
from unittest.mock import patch

from fastapi import FastAPI
from fastapi.testclient import TestClient
from ldap3 import MODIFY_DELETE

from app.adapters.ldap_adapter import LDAPAdapter

with patch.object(
    LDAPAdapter,
    "connect",
    return_value=True,
):
    from app.api import service_controller


def ldap_entry(**attributes):
    return SimpleNamespace(
        **{
            name: SimpleNamespace(value=value)
            for name, value in attributes.items()
        }
    )


class FakeConnection:
    def __init__(self):
        self.filters = []
        self.result = {"description": "success"}
        self.group_email_results = [
            ldap_entry(
                name="Staff",
                cn="Staff",
                mail="staff@example.com",
                description="",
                distinguishedName=(
                    "CN=Staff,OU=Groups,DC=example,DC=com"
                ),
            )
        ]
        self.group_name_results = []
        self.group_member_results = []
        self.computer_results = [
            ldap_entry(
                name="PC001",
                sAMAccountName="PC001$",
                distinguishedName=(
                    "CN=PC001,OU=Computers,DC=example,DC=com"
                ),
            )
        ]
        self.modify_calls = []
        self.ou_results = [
            ldap_entry(
                ou="Users",
                distinguishedName=(
                    "OU=Users,OU=HQ,DC=example,DC=com"
                ),
            ),
            ldap_entry(
                ou="Users",
                distinguishedName=(
                    "OU=Users,OU=Remote,DC=example,DC=com"
                ),
            ),
        ]

    def search(
        self,
        search_base,
        search_filter,
        attributes,
        size_limit,
    ):
        self.filters.append(search_filter)

        if "(objectClass=group)" in search_filter:
            if "(mail=staff@example.com)" in search_filter:
                self.entries = self.group_email_results
            elif "(mail=nested@example.com)" in search_filter:
                self.entries = self.group_member_results
            elif "(name=Nested)" in search_filter:
                self.entries = self.group_member_results
            elif "(name=Staff)" in search_filter:
                self.entries = self.group_name_results
            else:
                self.entries = []
        elif "(objectClass=computer)" in search_filter:
            self.entries = self.computer_results
        elif (
            "(objectCategory=person)" in search_filter
            and "(objectClass=user)" in search_filter
        ):
            self.entries = [
                ldap_entry(
                    sAMAccountName="auser",
                    distinguishedName=(
                        "CN=A User,OU=Users,DC=example,DC=com"
                    ),
                )
            ]
        elif "(objectClass=organizationalUnit)" in search_filter:
            if (
                "(ou=Users)" in search_filter
                or "(ou=UniqueOU)" in search_filter
            ):
                self.entries = self.ou_results
            elif (
                "(distinguishedName="
                "OU=Users,OU=HQ,DC=example,DC=com)"
                in search_filter
            ):
                self.entries = [self.ou_results[0]]
            else:
                self.entries = []
        else:
            self.entries = []

        return True

    def modify(self, dn, changes):
        self.modify_calls.append((dn, changes))
        return True


class FakeLdapAdapter:
    def __init__(self):
        self.calls = []
        self.connection = FakeConnection()

    def __getattr__(self, method_name):
        def action(*args, **kwargs):
            self.calls.append(
                (method_name, args, kwargs)
            )
            return {
                "success": True,
                "action": method_name,
            }

        return action


class ServiceControllerAdTests(unittest.TestCase):
    def setUp(self):
        self.fake_ldap = FakeLdapAdapter()
        self.ldap_patch = patch.object(
            service_controller,
            "ldap",
            self.fake_ldap,
        )
        self.ldap_patch.start()

        self.app = FastAPI()
        self.app.include_router(
            service_controller.router,
            prefix="/api/v1/service",
        )
        self.app.dependency_overrides[
            service_controller.require_integration_token
        ] = lambda: {"sub": "test-client"}
        self.client = TestClient(self.app)

    def tearDown(self):
        self.client.close()
        self.ldap_patch.stop()

    def test_kept_integration_routes_dispatch_as_before(self):
        routes = [
            (
                "/integration/ad/users/create",
                {
                    "employee_id": "E123",
                    "first_name": "A",
                    "last_name": "User",
                    "full_name": "A User",
                    "sam_account_name": "auser",
                    "password": "Example-password-123!",
                    "target_ou_dn": "OU=Users,DC=example,DC=com",
                    "title": "Engineer",
                    "department": "IT",
                },
                "create_user",
            ),
            (
                "/integration/ad/users/disable",
                {"sam_account_name": "auser"},
                "disable_user",
            ),
            (
                "/integration/ad/users/enable",
                {"sam_account_name": "auser"},
                "enable_user",
            ),
            (
                "/integration/ad/users/update-display-name",
                {"sam_account_name": "auser", "new_value": "A User"},
                "update_user_displayname",
            ),
            (
                "/integration/ad/users/update-department",
                {"sam_account_name": "auser", "new_value": "IT"},
                "update_user_department",
            ),
            (
                "/integration/ad/users/update-ip-phone",
                {"sam_account_name": "auser", "new_value": "1234"},
                "update_user_ip_phone",
            ),
            (
                "/integration/ad/users/update-description",
                {"sam_account_name": "auser", "new_value": "Employee"},
                "update_user_description",
            ),
            (
                "/integration/ad/computers/disable",
                {"computer_name": "PC001"},
                "disable_computer",
            ),
            (
                "/integration/ad/groups/create",
                {
                    "group_name": "Staff",
                    "target_ou_dn": "OU=Groups,DC=example,DC=com",
                },
                "create_group",
            ),
        ]

        for path, payload, expected_action in routes:
            with self.subTest(path=path):
                response = self.client.post(
                    f"/api/v1/service{path}",
                    json=payload,
                )
                self.assertEqual(response.status_code, 200)
                self.assertEqual(
                    response.json()["action"],
                    expected_action,
                )

        self.assertEqual(
            [call[0] for call in self.fake_ldap.calls],
            [route[2] for route in routes],
        )
        self.assertEqual(
            self.fake_ldap.calls[0][2],
            {
                "approved_by": "test-client",
                "approved_name": "test-client",
                "approval_type": "INTEGRATION",
            },
        )
        self.assertEqual(
            self.fake_ldap.calls[0][1][0].display_name,
            "A User",
        )
        self.assertTrue(
            self.fake_ldap.calls[0][1][0].dry_run
        )

    def test_group_add_and_remove_resolve_email_before_name(self):
        self.fake_ldap.connection.group_name_results = [
            ldap_entry(
                name="Staff",
                cn="Staff",
                mail="",
                description="",
                distinguishedName=(
                    "CN=Staff,OU=Legacy,DC=example,DC=com"
                ),
            ),
            ldap_entry(
                name="Staff",
                cn="Staff",
                mail="",
                description="",
                distinguishedName=(
                    "CN=Staff,OU=Groups,DC=example,DC=com"
                ),
            ),
        ]

        for suffix, action in [
            ("add", "add_group_member_by_dn"),
            ("remove", "remove_group_member_by_dn"),
        ]:
            with self.subTest(action=action):
                response = self.client.post(
                    f"/api/v1/service/integration/ad/group-members/{suffix}",
                    json={
                        "sam_account_name": "auser",
                        "target_group": "Staff",
                        "target_group_email": "staff@example.com",
                        "target_group_ou": "Groups",
                    },
                )

                self.assertEqual(response.status_code, 200)
                self.assertEqual(
                    self.fake_ldap.calls[-1][0],
                    action,
                )
                self.assertEqual(
                    self.fake_ldap.calls[-1][1],
                    (
                        "auser",
                        "CN=Staff,OU=Groups,DC=example,DC=com",
                    ),
                )

        self.assertEqual(
            self.fake_ldap.connection.filters,
            [
                "(&(objectClass=group)(mail=staff@example.com))",
                "(&(objectClass=group)(mail=staff@example.com))",
            ],
        )

    def test_group_name_is_fallback_when_email_does_not_match(self):
        self.fake_ldap.connection.group_email_results = []
        self.fake_ldap.connection.group_name_results = [
            ldap_entry(
                name="Staff",
                cn="Staff",
                mail="",
                description="",
                distinguishedName=(
                    "CN=Staff,OU=Groups,DC=example,DC=com"
                ),
            )
        ]

        response = self.client.post(
            "/api/v1/service/integration/ad/group-members/add",
            json={
                "sam_account_name": "auser",
                "target_group": "Staff",
                "target_group_email": "unknown@example.com",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            self.fake_ldap.connection.filters,
            [
                "(&(objectClass=group)(mail=unknown@example.com))",
                "(&(objectClass=group)(name=Staff))",
            ],
        )
        self.assertEqual(
            self.fake_ldap.calls[-1][1][1],
            "CN=Staff,OU=Groups,DC=example,DC=com",
        )

    def test_group_name_and_direct_parent_ou_resolve_exact_group(self):
        self.fake_ldap.connection.group_email_results = []
        self.fake_ldap.connection.group_name_results = [
            ldap_entry(
                name="Staff",
                cn="Staff",
                mail="",
                description="",
                distinguishedName=(
                    "CN=Staff,OU=Legacy,DC=example,DC=com"
                ),
            ),
            ldap_entry(
                name="Staff",
                cn="Staff",
                mail="",
                description="",
                distinguishedName=(
                    "CN=Staff,OU=Groups,DC=example,DC=com"
                ),
            ),
        ]

        response = self.client.post(
            "/api/v1/service/integration/ad/group-members/add",
            json={
                "sam_account_name": "auser",
                "target_group": "Staff",
                "target_group_ou": "Groups",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            self.fake_ldap.calls[-1][1][1],
            "CN=Staff,OU=Groups,DC=example,DC=com",
        )

    def test_add_computer_to_target_group(self):
        response = self.client.post(
            "/api/v1/service/integration/ad/group-members/add",
            json={
                "object_type": "computer",
                "computer_name": "PC001",
                "target_group_email": "staff@example.com",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json()["object_type"],
            "computer",
        )
        self.assertEqual(
            self.fake_ldap.connection.modify_calls[0][0],
            "CN=Staff,OU=Groups,DC=example,DC=com",
        )
        self.assertEqual(
            self.fake_ldap.connection.modify_calls[0][1]["member"][0][1],
            ["CN=PC001,OU=Computers,DC=example,DC=com"],
        )

    def test_add_nested_group_to_target_group(self):
        self.fake_ldap.connection.group_member_results = [
            ldap_entry(
                name="Nested",
                cn="Nested",
                mail="nested@example.com",
                description="",
                distinguishedName=(
                    "CN=Nested,OU=Groups,DC=example,DC=com"
                ),
            )
        ]

        response = self.client.post(
            "/api/v1/service/integration/ad/group-members/add",
            json={
                "object_type": "group",
                "member_group_email": "nested@example.com",
                "target_group_email": "staff@example.com",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json()["object_type"],
            "group",
        )
        self.assertEqual(
            self.fake_ldap.connection.modify_calls[0][0],
            "CN=Staff,OU=Groups,DC=example,DC=com",
        )
        self.assertEqual(
            self.fake_ldap.connection.modify_calls[0][1]["member"][0][1],
            ["CN=Nested,OU=Groups,DC=example,DC=com"],
        )

    def test_remove_computer_from_target_group(self):
        response = self.client.post(
            "/api/v1/service/integration/ad/group-members/remove",
            json={
                "object_type": "computer",
                "computer_name": "PC001",
                "target_group_email": "staff@example.com",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json()["action"],
            "remove_group_member",
        )
        self.assertEqual(
            self.fake_ldap.connection.modify_calls[0][0],
            "CN=Staff,OU=Groups,DC=example,DC=com",
        )
        self.assertEqual(
            self.fake_ldap.connection.modify_calls[0][1]["member"][0],
            (
                MODIFY_DELETE,
                ["CN=PC001,OU=Computers,DC=example,DC=com"],
            ),
        )

    def test_remove_nested_group_from_target_group(self):
        self.fake_ldap.connection.group_member_results = [
            ldap_entry(
                name="Nested",
                cn="Nested",
                mail="nested@example.com",
                description="",
                distinguishedName=(
                    "CN=Nested,OU=Groups,DC=example,DC=com"
                ),
            )
        ]

        response = self.client.post(
            "/api/v1/service/integration/ad/group-members/remove",
            json={
                "object_type": "group",
                "member_group_email": "nested@example.com",
                "target_group_email": "staff@example.com",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json()["action"],
            "remove_group_member",
        )
        self.assertEqual(
            self.fake_ldap.connection.modify_calls[0][0],
            "CN=Staff,OU=Groups,DC=example,DC=com",
        )
        self.assertEqual(
            self.fake_ldap.connection.modify_calls[0][1]["member"][0],
            (
                MODIFY_DELETE,
                ["CN=Nested,OU=Groups,DC=example,DC=com"],
            ),
        )

    def test_move_to_ou_resolves_target_and_dispatches_by_object_type(self):
        self.fake_ldap.connection.ou_results = [
            ldap_entry(
                ou="Users",
                distinguishedName=(
                    "OU=Users,OU=HQ,DC=example,DC=com"
                ),
            )
        ]

        requests = [
            (
                {
                    "object_type": "user",
                    "sam_account_name": "auser",
                    "target_ou": "Users",
                    "target_ou_parent": "HQ",
                },
                "move_user_to_ou",
                "auser",
            ),
            (
                {
                    "object_type": "computer",
                    "computer_name": "PC001",
                    "target_ou": "Users",
                    "target_ou_parent": "HQ",
                },
                "move_computer_to_ou",
                "PC001",
            ),
            (
                {
                    "object_type": "group",
                    "group_name": "Staff",
                    "target_ou": "Users",
                    "target_ou_parent": "HQ",
                },
                "move_group_to_ou",
                "Staff",
            ),
        ]

        for payload, action, identity in requests:
            with self.subTest(object_type=payload["object_type"]):
                response = self.client.post(
                    "/api/v1/service/integration/ad/move-to-ou",
                    json=payload,
                )

                self.assertEqual(response.status_code, 200)
                self.assertEqual(
                    self.fake_ldap.calls[-1][0],
                    action,
                )
                self.assertEqual(
                    self.fake_ldap.calls[-1][1],
                    (
                        identity,
                        "OU=Users,OU=HQ,DC=example,DC=com",
                    ),
                )

    def test_ambiguous_group_stops_before_ldap_mutation(self):
        self.fake_ldap.connection.group_email_results *= 2

        response = self.client.post(
            "/api/v1/service/integration/ad/group-members/add",
            json={
                "sam_account_name": "auser",
                "target_group_email": "staff@example.com",
            },
        )

        self.assertEqual(response.status_code, 409)
        self.assertEqual(self.fake_ldap.calls, [])

    def test_invalid_ou_stops_before_ldap_mutation(self):
        self.fake_ldap.connection.ou_results = []

        response = self.client.post(
            "/api/v1/service/integration/ad/move-to-ou",
            json={
                "object_type": "user",
                "sam_account_name": "auser",
                "target_ou": "Missing",
            },
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(self.fake_ldap.calls, [])

    def test_ou_name_and_direct_parent_disambiguate_target(self):
        response = self.client.post(
            "/api/v1/service/integration/ad/move-to-ou",
            json={
                "object_type": "user",
                "sam_account_name": "auser",
                "target_ou": "Users",
                "target_ou_parent": "HQ",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            self.fake_ldap.calls[-1][1][1],
            "OU=Users,OU=HQ,DC=example,DC=com",
        )
        self.assertEqual(
            self.fake_ldap.connection.filters,
            [
                "(&(objectClass=organizationalUnit)(ou=Users))"
            ],
        )

    def test_ou_email_is_rejected_by_integration_contract(self):
        response = self.client.post(
            "/api/v1/service/integration/ad/move-to-ou",
            json={
                "object_type": "user",
                "sam_account_name": "auser",
                "target_ou": "Users",
                "target_ou_email": "users@example.com",
            },
        )

        self.assertEqual(response.status_code, 422)
        self.assertEqual(self.fake_ldap.calls, [])

    def test_move_to_ou_accepts_and_resolves_dn_in_target_ou(self):
        response = self.client.post(
            "/api/v1/service/integration/ad/move-to-ou",
            json={
                "object_type": "user",
                "sam_account_name": "auser",
                "target_ou": "OU=Users,OU=HQ,DC=example,DC=com",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            self.fake_ldap.connection.filters,
            [
                "(&(objectClass=organizationalUnit)"
                "(distinguishedName=OU=Users,OU=HQ,DC=example,DC=com))"
            ],
        )
        self.assertEqual(
            self.fake_ldap.calls[-1][1][1],
            "OU=Users,OU=HQ,DC=example,DC=com",
        )

    def test_move_to_ou_requires_target_ou_and_parent_is_optional(self):
        response = self.client.post(
            "/api/v1/service/integration/ad/move-to-ou",
            json={
                "object_type": "user",
                "sam_account_name": "auser",
            },
        )

        self.assertEqual(response.status_code, 422)
        self.assertEqual(self.fake_ldap.calls, [])

        self.fake_ldap.connection.ou_results = [
            ldap_entry(
                ou="UniqueOU",
                distinguishedName=(
                    "OU=UniqueOU,OU=HQ,DC=example,DC=com"
                ),
            )
        ]

        response = self.client.post(
            "/api/v1/service/integration/ad/move-to-ou",
            json={
                "object_type": "user",
                "sam_account_name": "auser",
                "target_ou": "UniqueOU",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            self.fake_ldap.calls[-1][1],
            (
                "auser",
                "OU=UniqueOU,OU=HQ,DC=example,DC=com",
            ),
        )

    def test_duplicate_integration_routes_are_removed(self):
        paths = {
            route.path
            for route in service_controller.router.routes
        }
        prefix = "/integration/ad/"

        integration_task_routes = {
            path
            for path in paths
            if path.startswith(prefix)
            and (
                "group-members" in path
                or "move" in path
            )
        }

        self.assertEqual(
            integration_task_routes,
            {
                "/integration/ad/group-members/add",
                "/integration/ad/group-members/remove",
                "/integration/ad/move-to-ou",
            },
        )

    def test_integration_ad_route_requires_token(self):
        self.app.dependency_overrides.clear()

        response = self.client.post(
            "/api/v1/service/integration/ad/group-members/add",
            json={
                "sam_account_name": "auser",
                "target_group": "Staff",
            },
            headers={"Authorization": "Bearer invalid"},
        )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(self.fake_ldap.calls, [])

    def test_create_user_enable_step_targets_the_new_user_dn(self):
        class Connection:
            result = {"description": "success"}

            def __init__(self):
                self.modified_dn = None

            def modify(self, dn, attributes):
                self.modified_dn = dn
                self.attributes = attributes
                return True

        connection = Connection()
        adapter = LDAPAdapter()
        adapter.connection = connection

        enabled = adapter._enable_user_by_dn(
            "CN=A User,OU=Users,DC=example,DC=com"
        )

        self.assertTrue(enabled)
        self.assertEqual(
            connection.modified_dn,
            "CN=A User,OU=Users,DC=example,DC=com",
        )

    def test_existing_offboarding_routes_keep_their_behavior(self):
        request = {
            "employee_id": "E123",
            "email": "a.user@example.com",
            "reason": "Leaving",
        }
        expected = {"request_id": "REQ-1"}

        with patch.object(
            service_controller,
            "create_offboarding_plan",
            return_value=expected,
        ) as create_plan:
            self.app.dependency_overrides[
                service_controller.require_service_token
            ] = lambda: {"sub": "service"}

            service_response = self.client.post(
                "/api/v1/service/employee-offboarding",
                json=request,
            )
            integration_response = self.client.post(
                "/api/v1/service/integration/employee-offboarding",
                json=request,
            )

        self.assertEqual(service_response.status_code, 200)
        self.assertEqual(integration_response.status_code, 200)
        self.assertEqual(service_response.json(), expected)
        self.assertEqual(integration_response.json(), expected)
        self.assertEqual(create_plan.call_count, 2)


if __name__ == "__main__":
    unittest.main()
