from datetime import datetime, timezone

from conductor.domain.enums import TaskPriority
from conductor.domain.task import Task


PRIORITY_ORDER = {
    TaskPriority.HIGH: 0,
    TaskPriority.NORMAL: 1,
    TaskPriority.LOW: 2,
}


def effective_priority(
    task: Task,
    now: datetime | None = None,
) -> int:

    if task.ready_since is None:
        return PRIORITY_ORDER[task.priority]

    now = now or datetime.now(timezone.utc)

    if task.ready_since.tzinfo is None or now.tzinfo is None:
        raise ValueError("Timestamps must be timezone-aware")

    waiting_minutes = (
        now - task.ready_since
    ).total_seconds() / 60

    promotions = max(0, int(waiting_minutes // 30))

    return max(
        0,
        PRIORITY_ORDER[task.priority] - promotions,
    )