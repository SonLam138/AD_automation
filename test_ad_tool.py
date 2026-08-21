from app.adapters.ldap_adapter import LDAPAdapter
from app.config import (
	LDAP_HOST,
	LDAP_USER,
	LDAP_PASSWORD
)


# TEST CONFIGURATION
RUN_TEST = "create_group"

GROUP_NAME = "workflow_grp"
GROUP_OU_DN = "OU=Group,DC=automate,DC=com,DC=vn"
GROUP_DESCRIPTION = "Test"
COMPUTER_NAME = "WF_001"


def validate_configuration():

	if RUN_TEST not in TEST_MAP:
		raise ValueError(
			"Set RUN_TEST to one of: "
			"create_group, move_group_to_ou, "
			"move_computer_to_group"
		)

	if not GROUP_NAME:
		raise ValueError(
			"GROUP_NAME is required"
		)

	if RUN_TEST in (
		"create_group",
		"move_group_to_ou"
	) and not GROUP_OU_DN:
		raise ValueError(
			"GROUP_OU_DN is required"
		)

	if RUN_TEST == "move_computer_to_group" and not COMPUTER_NAME:
		raise ValueError(
			"COMPUTER_NAME is required"
		)


ldap = LDAPAdapter()


def test_create_group():

	result = ldap.create_group(
		group_name=GROUP_NAME,
		target_ou_dn=GROUP_OU_DN,
		description=GROUP_DESCRIPTION or None
	)

	print(result)


def test_move_group_to_ou():

	result = ldap.move_group_to_ou(
		group_name=GROUP_NAME,
		target_ou_dn=GROUP_OU_DN
	)

	print(result)


def test_move_computer_to_group():

	result = ldap.move_computer_to_group(
		computer_name=COMPUTER_NAME,
		group_name=GROUP_NAME
	)

	print(result)


TEST_MAP = {
	"create_group": test_create_group,
	"move_group_to_ou": test_move_group_to_ou,
	"move_computer_to_group": test_move_computer_to_group
}


if __name__ == "__main__":

	validate_configuration()

	ldap.connect(
		LDAP_HOST,
		LDAP_USER,
		LDAP_PASSWORD
	)

	TEST_MAP[RUN_TEST]()
