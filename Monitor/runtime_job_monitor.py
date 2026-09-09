import json
import os
import threading

from app.event.monitor_bus import (
    publish_monitor_refresh,
)


RUNTIME_JOB_MONITOR_FILE = os.path.join(
    os.path.dirname(__file__),
    "runtime_job_monitor.json"
)


_snapshot_lock = threading.Lock()


SUPPORTED_JOB_EVENTS = {
    "JOB_CREATED",
    "JOB_STARTED",
    "JOB_COMPLETED",
    "JOB_FAILED",
}


def build_empty_runtime_job_snapshot():

    return {
        "total_jobs_created":
            0,

        "failed_jobs_count":
            0,

        "last_executed_job":
            None,

        #
        # Chỉ giữ 5 Job mới nhất trong queue.
        #

        "queued_jobs":
            [],

        #
        # Chỉ giữ đúng 5 lỗi mới nhất.
        #

        "recent_failed_jobs":
            [],
    }


def normalize_runtime_job_snapshot(
    data: dict,
):

    empty_snapshot = (
        build_empty_runtime_job_snapshot()
    )

    for key, default_value in (
        empty_snapshot.items()
    ):

        if key not in data:

            data[
                key
            ] = default_value

    return data


def load_runtime_job_snapshot():

    if not os.path.exists(
        RUNTIME_JOB_MONITOR_FILE
    ):

        return (
            build_empty_runtime_job_snapshot()
        )

    try:

        with open(
            RUNTIME_JOB_MONITOR_FILE,
            "r",
            encoding="utf-8",
        ) as file:

            content = (
                file.read()
                .strip()
            )

            if not content:

                return (
                    build_empty_runtime_job_snapshot()
                )

            data = json.loads(
                content
            )

            return (
                normalize_runtime_job_snapshot(
                    data
                )
            )

    except Exception as ex:

        print(
            "LOAD RUNTIME JOB SNAPSHOT ERROR =",
            repr(ex),
        )

        return (
            build_empty_runtime_job_snapshot()
        )


def write_runtime_job_snapshot(
    data: dict,
):

    temp_file = (
        RUNTIME_JOB_MONITOR_FILE
        +
        ".tmp"
    )

    try:

        with open(
            temp_file,
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                data,
                file,
                ensure_ascii=False,
                indent=4,
                default=str,
            )

        os.replace(
            temp_file,
            RUNTIME_JOB_MONITOR_FILE,
        )

    except Exception:

        if os.path.exists(
            temp_file
        ):

            os.remove(
                temp_file
            )

        raise

    return data


def build_snapshot_job_view(
    event: dict,
):

    return {
        "job_id":
            event.get(
                "job_id"
            ),

        "action_code":
            event.get(
                "action_code"
            ),

        "display_name":
            event.get(
                "display_name"
            ),

        "object_name":
            event.get(
                "object_name"
            ),

        "target":
            event.get(
                "target"
            ),

        "execute_at":
            event.get(
                "execute_at"
            ),

        "status":
            event.get(
                "status"
            ),

        "error_message":
            event.get(
                "error_message"
            ),

        "timestamp":
            event.get(
                "timestamp"
            ),
    }


def normalize_queued_jobs(
    queued_jobs,
):
    unique_jobs = {}

    for job in queued_jobs:
        job_id = job.get("job_id")

        if not job_id:
            continue

        if job_id not in unique_jobs:
            unique_jobs[job_id] = job

    return list(
        unique_jobs.values()
    )[:5]


def remove_job_from_queue(
    queued_jobs,
    job_id,
):
    return [
        item
        for item in queued_jobs
        if item.get("job_id") != job_id
    ]


def update_runtime_job_from_event(
    event: dict,
):

    event_name = (
        event.get(
            "event_name"
        )
    )

    if (
        event_name
        not in
        SUPPORTED_JOB_EVENTS
    ):

        return None

    with _snapshot_lock:

        data = (
            load_runtime_job_snapshot()
        )

        #
        # JOB_CREATED
        #
        # - Total +1
        # - Thêm vào runtime queue
        #

        if event_name == "JOB_CREATED":

            data[
                "total_jobs_created"
            ] = (
                int(
                    data.get(
                        "total_jobs_created",
                        0,
                    )
                )
                +
                1
            )

            queued_jobs = list(
                data.get(
                    "queued_jobs",
                    []
                )
            )

            created_job = (
                build_snapshot_job_view(
                    event
                )
            )

            #
            # Không thêm trùng job_id.
            #

            queued_jobs = [
                item
                for item in queued_jobs
                if (
                    item.get(
                        "job_id"
                    )
                    !=
                    created_job.get(
                        "job_id"
                    )
                )
            ]

            queued_jobs.insert(
                0,
                created_job,
            )

            #
            # Queue giữ 5 Job mới nhất theo thứ tự event.
            #

            data[
                "queued_jobs"
            ] = normalize_queued_jobs(
                queued_jobs
            )

        #
        # JOB_STARTED
        #
        # Job đã bắt đầu chạy nên không còn là
        # một trong các Job "sắp chạy".
        #

        elif event_name == "JOB_STARTED":

            started_job_id = (
                event.get(
                    "job_id"
                )
            )

            queued_jobs = list(
                data.get(
                    "queued_jobs",
                    []
                )
            )

            data[
                "queued_jobs"
            ] = remove_job_from_queue(
                queued_jobs,
                started_job_id,
            )

        #
        # JOB_COMPLETED
        #
        # Ghi đè Job vừa thực thi gần nhất.
        #

        elif event_name == "JOB_COMPLETED":

            completed_job_id = (
                event.get(
                    "job_id"
                )
            )

            data[
                "last_executed_job"
            ] = (
                build_snapshot_job_view(
                    event
                )
            )

            data[
                "queued_jobs"
            ] = remove_job_from_queue(
                data.get(
                    "queued_jobs",
                    []
                ),
                completed_job_id,
            )

        #
        # JOB_FAILED
        #
        # - Ghi đè Last Executed Job
        # - Failed count +1
        # - Chèn vào đầu danh sách lỗi
        # - Chỉ giữ 5 lỗi gần nhất
        #

        elif event_name == "JOB_FAILED":

            failed_job = (
                build_snapshot_job_view(
                    event
                )
            )

            data[
                "queued_jobs"
            ] = remove_job_from_queue(
                data.get(
                    "queued_jobs",
                    []
                ),
                failed_job.get(
                    "job_id"
                ),
            )

            data[
                "last_executed_job"
            ] = failed_job

            data[
                "failed_jobs_count"
            ] = (
                int(
                    data.get(
                        "failed_jobs_count",
                        0,
                    )
                )
                +
                1
            )

            recent_failed_jobs = list(
                data.get(
                    "recent_failed_jobs",
                    []
                )
            )

            recent_failed_jobs = [
                item
                for item in recent_failed_jobs
                if (
                    item.get(
                        "job_id"
                    )
                    !=
                    failed_job.get(
                        "job_id"
                    )
                )
            ]

            recent_failed_jobs.insert(
                0,
                failed_job,
            )

            data[
                "recent_failed_jobs"
            ] = (
                recent_failed_jobs[
                    :5
                ]
            )

        data[
            "queued_jobs"
        ] = normalize_queued_jobs(
            data.get(
                "queued_jobs",
                []
            )
        )

        result = (
            write_runtime_job_snapshot(
                data
            )
        )

    publish_monitor_refresh()

    return result


def get_runtime_job_snapshot():

    with _snapshot_lock:

        data = (
            load_runtime_job_snapshot()
        )

        queued_jobs = list(
            data.get(
                "queued_jobs",
                []
            )
        )

        queued_jobs = normalize_queued_jobs(
            queued_jobs
        )

        data[
            "queued_jobs"
        ] = queued_jobs

        write_runtime_job_snapshot(
            data
        )

        return {
            "total_jobs_created":
                data.get(
                    "total_jobs_created",
                    0,
                ),

            "failed_jobs_count":
                data.get(
                    "failed_jobs_count",
                    0,
                ),

            "last_executed_job":
                data.get(
                    "last_executed_job"
                ),

            #
            # Dashboard chỉ thấy đúng
            # 5 Job sắp chạy gần nhất.
            #

            "next_jobs":
                queued_jobs,

            "recent_failed_jobs":
                data.get(
                    "recent_failed_jobs",
                    []
                ),
        }