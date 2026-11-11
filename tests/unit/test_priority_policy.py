from datetime import datetime, timedelta, timezone

from conductor.domain.enums import TaskPriority
from conductor.domain.task import Task
from conductor.services.priority_policy import effective_priority


def test_low_priority_task_gets_promoted_after_30_minutes():
    now = datetime.now(timezone.utc)

    task = Task(
        "P1",
        "Documentation",
        priority=TaskPriority.LOW,
        ready_since=now - timedelta(minutes=30),
    )

    assert effective_priority(task, now) == 1


def test_low_priority_task_becomes_high_after_60_minutes():
    now = datetime.now(timezone.utc)

    task = Task(
        "P1",
        "Documentation",
        priority=TaskPriority.LOW,
        ready_since=now - timedelta(minutes=60),
    )

    assert effective_priority(task, now) == 0


def test_task_without_ready_timestamp_keeps_original_priority():
    task = Task(
        "P1",
        "Documentation",
        priority=TaskPriority.LOW,
    )

    assert effective_priority(task) == 2