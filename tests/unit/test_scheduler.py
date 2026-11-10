from conductor.domain.task import Task
from conductor.domain.enums import TaskPriority
from conductor.services.scheduler import select_tasks


def test_scheduler_respects_available_slots():
    tasks = [
        Task("P1", "Task A", id="A"),
        Task("P1", "Task B", id="B"),
        Task("P1", "Task C", id="C"),
    ]

    selected = select_tasks(tasks, 2)

    assert len(selected) == 2


def test_scheduler_prioritizes_high_priority_tasks():
    tasks = [
        Task("P1", "Low task", id="A", priority=TaskPriority.LOW),
        Task("P1", "High task", id="B", priority=TaskPriority.HIGH),
        Task("P1", "Normal task", id="C", priority=TaskPriority.NORMAL),
    ]

    selected = select_tasks(tasks, 1)

    assert selected[0].id == "B"


def test_scheduler_returns_empty_when_no_slots():
    tasks = [
        Task("P1", "Task A", id="A"),
    ]

    assert select_tasks(tasks, 0) == []