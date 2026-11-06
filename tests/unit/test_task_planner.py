from conductor.domain.task import Task
from conductor.services.task_planner import find_ready_tasks


def create_tasks():
    return [
        Task(id="A", project_id="P1", description="Create database schema"),
        Task(
            id="B",
            project_id="P1",
            description="Implement API",
            dependencies=("A",),
        ),
        Task(
            id="C",
            project_id="P1",
            description="Write API tests",
            dependencies=("B",),
        ),
        Task(
            id="D",
            project_id="P1",
            description="Update documentation",
            dependencies=("A",),
        ),
    ]


def test_only_independent_task_is_ready_initially():
    tasks = create_tasks()

    ready = find_ready_tasks(tasks, set())

    assert [task.id for task in ready] == ["A"]


def test_parallel_tasks_become_ready_after_a():
    tasks = create_tasks()

    ready = find_ready_tasks(tasks, {"A"})

    assert {task.id for task in ready} == {"B", "D"}


def test_c_becomes_ready_after_b():
    tasks = create_tasks()

    ready = find_ready_tasks(tasks, {"A", "B"})

    assert {task.id for task in ready} == {"C", "D"}