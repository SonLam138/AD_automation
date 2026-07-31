# app/utils/perf.py

import time
import uuid


class PerfTimer:
    def __init__(
        self,
        scope: str,
        trace_id: str | None = None
    ):
        self.scope = scope
        self.trace_id = (
            trace_id
            or str(uuid.uuid4())[:8]
        )

        self.start = time.perf_counter()
        self.last = self.start

    def checkpoint(
        self,
        name: str
    ):
        now = time.perf_counter()

        step = now - self.last
        total = now - self.start

        print(
            f"[PERF][{self.scope}][{self.trace_id}] "
            f"{name} | "
            f"step={step:.3f}s | "
            f"total={total:.3f}s"
        )

        self.last = now

    def finish(
        self,
        name: str = "FINISH"
    ):
        now = time.perf_counter()

        total = now - self.start

        print(
            f"[PERF][{self.scope}][{self.trace_id}] "
            f"{name} | "
            f"total={total:.3f}s"
        )