from conductor.domain.enums import TaskStatus
from conductor.domain.task import Task


def find_ready_tasks(
    tasks: list[Task],
    completed_task_ids: set[str],
) -> list[Task]:

    return [
        task
        for task in tasks
        if (
            task.status == TaskStatus.PENDING
            and task.id not in completed_task_ids
            and all(
                dependency_id in completed_task_ids
                for dependency_id in task.dependencies
            )
        )
    ]