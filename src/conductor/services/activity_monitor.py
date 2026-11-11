from datetime import datetime, timedelta, timezone
from enum import Enum


class ProcessActivity(str, Enum):
    ACTIVE = "active"
    QUIET = "quiet"
    EXITED = "exited"


def get_process_activity(
    last_output_at: datetime | None,
    now: datetime,
    idle_threshold_seconds: int,
    is_running: bool = True,
) -> ProcessActivity:

    if not is_running:
        return ProcessActivity.EXITED

    if idle_threshold_seconds <= 0:
        raise ValueError("Idle threshold must be positive")

    if last_output_at is None:
        return ProcessActivity.QUIET

    if last_output_at.tzinfo is None or now.tzinfo is None:
        raise ValueError("Timestamps must be timezone-aware")

    idle_time = now - last_output_at

    if idle_time >= timedelta(seconds=idle_threshold_seconds):
        return ProcessActivity.QUIET

    return ProcessActivity.ACTIVE