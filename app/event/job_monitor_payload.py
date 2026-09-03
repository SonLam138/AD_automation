from typing import Any, Dict


def build_job_monitor_payload(
    job,
) -> Dict[str, Any]:

    business_data = (
        job.business_data
        or {}
    )

    #
    # ==========================================
    # OBJECT NAME
    # ==========================================
    #

    target_object = (
        business_data.get(
            "target_object",
            {}
        )
        or {}
    )

    object_name = (
        target_object.get(
            "computer_name"
        )
        or
        target_object.get(
            "display_name"
        )
        or
        target_object.get(
            "sam_account_name"
        )
        or
        target_object.get(
            "email"
        )
        or
        target_object.get(
            "dn"
        )
        or
        "Unknown"
    )

    #
    # ==========================================
    # TARGET
    # Support:
    # - action_data
    # - step_new_values
    # ==========================================
    #

    target = None

    action_data = (
        business_data.get(
            "action_data",
            {}
        )
        or {}
    )

    step_data = (
        action_data.get(
            job.action_id,
            {}
        )
        or {}
    )

    target = (
        step_data.get(
            "target_ou"
        )
        or
        step_data.get(
            "targetOu"
        )
        or
        step_data.get(
            "target_group"
        )
        or
        step_data.get(
            "targetGroup"
        )
        or
        step_data.get(
            "target_dn"
        )
        or
        step_data.get(
            "targetDn"
        )
        or
        step_data.get(
            "group_name"
        )
        or
        step_data.get(
            "groupName"
        )
    )

    #
    # Fallback schema Temp Access cũ
    #
    # step_new_values
    #

    if not target:

        step_new_values = (
            business_data.get(
                "step_new_values",
                []
            )
            or []
        )

        for item in step_new_values:

            if (
                item.get(
                    "step_id"
                )
                !=
                job.action_id
            ):
                continue

            target = (
                item.get(
                    "new_value"
                )
            )

            break

    #
    # ==========================================
    # EXECUTE AT
    # ==========================================
    #

    execute_at = None

    if getattr(
        job,
        "execute_at",
        None
    ):

        execute_at = (
            job.execute_at.isoformat()
            if hasattr(
                job.execute_at,
                "isoformat"
            )
            else str(
                job.execute_at
            )
        )

    return {
        "job_id":
            job.job_id,

        "action_code":
            job.action_code,

        "display_name":
            job.display_name,

        "object_name":
            object_name,

        "target":
            target,

        "execute_at":
            execute_at,
    }