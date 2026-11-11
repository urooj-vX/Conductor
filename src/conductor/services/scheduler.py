from conductor.domain.enums import TaskPriority
from conductor.domain.task import Task
from conductor.services.priority_policy import effective_priority
from conductor.services.scoring import calculate_scores


PRIORITY_ORDER = {
    TaskPriority.HIGH: 0,
    TaskPriority.NORMAL: 1,
    TaskPriority.LOW: 2,
}


def select_tasks(
    ready_tasks: list[Task],
    available_slots: int,
    impact: dict[str, int] | None = None,
) -> list[Task]:

    if available_slots < 0:
        raise ValueError("Available slots cannot be negative")

    scores = calculate_scores(ready_tasks, impact if impact is not None else {}) 
    ordered_tasks = sorted(
        ready_tasks,
        key=lambda task: (
            -scores[task.id],
            task.created_at,
            task.id,
        ),
    )

    return ordered_tasks[:available_slots]