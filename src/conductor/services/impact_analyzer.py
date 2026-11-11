from conductor.domain.task import Task


def calculate_downstream_impact(
    tasks: list[Task],
) -> dict[str, int]:

    dependents: dict[str, list[str]] = {
        task.id: [] for task in tasks
    }

    # Build reverse dependency relationships.
    for task in tasks:
        for dependency_id in task.dependencies:
            dependents[dependency_id].append(task.id)

    impact: dict[str, int] = {}

    for task in tasks:
        visited: set[str] = set()
        stack = list(dependents[task.id])

        while stack:
            dependent_id = stack.pop()

            if dependent_id in visited:
                continue

            visited.add(dependent_id)
            stack.extend(dependents[dependent_id])

        impact[task.id] = len(visited)

    return impact