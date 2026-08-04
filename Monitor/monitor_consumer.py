from Monitor.monitor_writer import write_search_record
from Monitor.runtime_monitor_writer import (
    update_runtime_from_event
)

class MonitorConsumer:
    """
    Monitor consumer listens to runtime events
    and builds search_monitor.jsonl records.

    It does not control runtime.
    It only catches useful events from the stream.
    """

    def __init__(self):
        self.current_context = {}

    def consume(
        self,
        event: dict
    ):
        event_name = event.get(
            "event_name"
        )
        update_runtime_from_event(
            event_name
        )
        if event_name == "QUERY_RECEIVED":
            self._handle_query_received(
                event
            )
            return

        if event_name == "DETECTION_RESULT":
            self._handle_detection_result(
                event
            )
            return

        if event_name == "ACTION_COMPLETED":
            self._handle_action_completed(
                event
            )
            return

        if event_name == "ACTION_FAILED":
            self._handle_action_failed(
                event
            )
            return

    def _handle_query_received(
        self,
        event: dict
    ):
        self.current_context = {
            "username": event.get(
                "username",
                "UNKNOWN"
            ),

            "query": event.get(
                "user_query",
                ""
            )
        }

    def _handle_detection_result(
        self,
        event: dict
    ):
        detected_keywords = event.get(
            "detected_keywords",
            {}
        ) or {}

        objects = []

        for object_type, object_name in detected_keywords.items():

            if not object_name:
                continue

            objects.append(
                {
                    "object_type": object_type,
                    "object_name": str(
                        object_name
                    )
                }
            )

        primary_object = None

        if objects:
            primary_object = objects[0]

        self.current_context.update(
            {
                "action": event.get(
                    "detected_action"
                ),

                "objects": objects,

                "object_type": (
                    primary_object.get(
                        "object_type"
                    )
                    if primary_object
                    else "UNKNOWN"
                ),

                "object_name": (
                    primary_object.get(
                        "object_name"
                    )
                    if primary_object
                    else "UNKNOWN"
                )
            }
        )

    def _handle_action_completed(
        self,
        event: dict
    ):
        self._write_final_record(
            event=event,
            result="SUCCESS"
        )

    def _handle_action_failed(
        self,
        event: dict
    ):
        self._write_final_record(
            event=event,
            result="FAILED"
        )

    def _write_final_record(
        self,
        event: dict,
        result: str
    ):
        action = (
            self.current_context.get(
                "action"
            )
            or event.get(
                "action"
            )
            or "UNKNOWN"
        )

        objects = self.current_context.get(
            "objects",
            []
        )

        object_type = self.current_context.get(
            "object_type",
            "UNKNOWN"
        )

        object_name = self.current_context.get(
            "object_name",
            "UNKNOWN"
        )

        metadata = {
            "event_id": event.get(
                "event_id"
            ),

            "execution_result": event.get(
                "execution_result"
            ),

            "error": event.get(
                "error"
            )
        }

        write_search_record(
            username=self.current_context.get(
                "username",
                "UNKNOWN"
            ),

            query=self.current_context.get(
                "query",
                ""
            ),

            action=action,

            object_type=object_type,

            object_name=object_name,

            result=result,

            metadata=metadata,

            objects=objects
        )

        self.current_context = {}


monitor_consumer = MonitorConsumer()


def consume_monitor_event(
    event: dict
):
    monitor_consumer.consume(
        event
    )