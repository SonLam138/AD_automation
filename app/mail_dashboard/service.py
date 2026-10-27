from app.event.monitor_bus import (
    publish_monitor_refresh,
)
from app.mail_dashboard.repository import (
    MailDashboardRepository,
)
from app.mail_dashboard.schemas import (
    MailDashboardSnapshot,
)


class MailDashboardService:
    def __init__(
        self,
        repository: MailDashboardRepository | None = None,
    ):
        self.repository = repository or MailDashboardRepository()

    def upsert_snapshot(
        self,
        snapshot: MailDashboardSnapshot,
    ) -> str:
        result = self.repository.upsert(snapshot)
        if result.changed:
            publish_monitor_refresh()
        return result.status

    def get_summary(self) -> dict:
        return self.repository.get_summary()
