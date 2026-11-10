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

    validate_no_cycles(tasks)


def validate_no_cycles(tasks: list[Task]) -> None:
    graph = {
        task.id: task.dependencies
        for task in tasks
    }

    # 0 = unvisited, 1 = visiting, 2 = visited
    state = {task_id: 0 for task_id in graph}

    for start_node in graph:

        if state[start_node] != 0:
            continue

        state[start_node] = 1

        # Each stack frame stores a node and its dependency iterator.
        stack = [(start_node, iter(graph[start_node]))]

        while stack:
            current_node, dependencies = stack[-1]

            try:
                dependency_id = next(dependencies)

            except StopIteration:
                state[current_node] = 2
                stack.pop()
                continue

            if state[dependency_id] == 1:
                raise ValueError("Circular dependency detected")

            if state[dependency_id] == 0:
                state[dependency_id] = 1

                stack.append(
                    (dependency_id, iter(graph[dependency_id]))
                )