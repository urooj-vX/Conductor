from conductor.domain.task import Task


def validate_dependencies(tasks: list[Task]) -> None:
    task_ids = {task.id for task in tasks}

    if len(task_ids) != len(tasks):
        raise ValueError("Duplicate task IDs found")

    for task in tasks:

        if task.id in task.dependencies:
            raise ValueError(
                f"Task {task.id} cannot depend on itself"
            )

        for dependency_id in task.dependencies:
            if dependency_id not in task_ids:
                raise ValueError(
                    f"Dependency {dependency_id} "
                    f"does not exist for task {task.id}"
                )