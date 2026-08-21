from app.auto_engine.models.base import (
    SourceAdapter,
)

from app.auto_engine.models.request_models import (
    Request,
)


class WorkflowRuntimeAdapter(
    SourceAdapter
):

    def parse(
        self,
        source_data
    ) -> Request:

        if isinstance(
            source_data,
            Request
        ):
            return source_data

        return Request(
            **source_data
        )