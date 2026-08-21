from app.search_tools.workflow_search_user import workflow_search_user
from app.search_tools.workflow_search_group import workflow_search_group
from app.search_tools.computer_search import search_computer
from app.adapters.ldap_container import (
    ldap
)
class CustomWorkflowValidationService:

    def _require_exactly_one(
        self,
        resolution: dict,
        alias: str,
        object_type: str
    ) -> dict:
        """
        Require a resolver to return exactly one object.

        Resolver contract:
        {
            "success": bool,
            "count": int,
            "results": list,
            ...
        }
        """

        if not resolution.get(
            "success"
        ):

            raise ValueError(
                resolution.get(
                    "message"
                )
                or (
                    f"{object_type} resolution failed "
                    f"for object '{alias}'"
                )
            )

        count = resolution.get(
            "count",
            0
        )

        results = resolution.get(
            "results",
            []
        )

        if count == 0:

            raise ValueError(
                f"{object_type} not found "
                f"for object '{alias}'"
            )

        if count > 1:

            raise ValueError(
                f"Multiple {object_type} objects matched "
                f"for object '{alias}'"
            )

        if len(results) != 1:

            raise ValueError(
                f"Invalid {object_type} resolver result "
                f"for object '{alias}'"
            )

        return results[0]

    def validate_objects(
        self,
        objects: list
    ):

        for obj in objects:

            object_type = obj.get(
                "objectType"
            )

            if object_type == "USER":
                self.validate_user(obj)

            elif object_type == "GROUP":
                self.validate_group(obj)

            elif object_type == "COMPUTER":
                self.validate_computer(obj)

            elif object_type in [
                "CREATE_NEW_USER",
                "CREATE_NEW_GROUP"
            ]:
                print(
                    f"[SKIP] "
                    f"{obj.get('alias')}"
                )

    def validate_user(
        self,
        obj: dict
    ) -> dict:

        lookup_request = (
            self.build_user_lookup_request(
                obj
            )
        )

        resolution = workflow_search_user(
            connection=ldap.connection,

            employee_id=(
                lookup_request.get(
                    "employee_id"
                )
            ),

            email=(
                lookup_request.get(
                    "email"
                )
            ),
        )

        return self._require_exactly_one(
            resolution=resolution,
            alias=obj.get(
                "alias",
                ""
            ),
            object_type="USER"
        )


    def build_user_lookup_request(
        self,
        obj: dict
    ):

        return {
            "object_type": "USER",

            "employee_id":
                (obj.get("employeeId") or "").strip(),

            "email":
                (obj.get("email") or "").strip(),

            "username":
                (obj.get("username") or "").strip()
        }

    def validate_group(
        self,
        obj: dict
    ) -> dict:

        lookup_request = (
            self.build_group_lookup_request(
                obj
            )
        )

        resolution = workflow_search_group(
            connection=ldap.connection,

            email=(
                lookup_request.get(
                    "email"
                )
            ),

            group_name=(
                lookup_request.get(
                    "group_name"
                )
            ),
        )

        return self._require_exactly_one(
            resolution=resolution,
            alias=obj.get(
                "alias",
                ""
            ),
            object_type="GROUP"
        )

    def build_group_lookup_request(
        self,
        obj: dict
    ):

        return {
            "object_type": "GROUP",

            "group_name":
                (obj.get("username") or "").strip()
        }

    def validate_computer(
        self,
        obj: dict
    ) -> dict:

        lookup_request = (
            self.build_computer_lookup_request(
                obj
            )
        )

        resolution = search_computer(
            connection=ldap.connection,

            keyword=(
                lookup_request.get(
                    "computer_name"
                )
            ),
        )

        return self._require_exactly_one(
            resolution=resolution,
            alias=obj.get(
                "alias",
                ""
            ),
            object_type="COMPUTER"
        )

    def build_computer_lookup_request(
        self,
        obj: dict
    ):

        return {
            "object_type": "COMPUTER",

            "computer_name":
                (obj.get("computerName") or "").strip()
        }






    def validate(
        self,
        workflow_info,
        objects
    ):
        try:

            self.validate_objects(
                objects
            )

            return {
                "success": True
            }

        except Exception as ex:

            return {
                "success": False,
                "message": str(ex)
            }