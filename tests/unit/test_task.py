from conductor.domain.task import Task
from conductor.domain.enums import TaskStatus


def test_task_creation():
    task = Task(
        project_id="project-001",
        description="Implement authentication",
    )

    assert task.project_id == "project-001"
    assert task.description == "Implement authentication"
    assert task.status == TaskStatus.PENDING
    assert task.dependencies == ()


def test_tasks_have_unique_ids():
    task_one = Task("project-001", "Build API")
    task_two = Task("project-001", "Write tests")

    assert task_one.id != task_two.id


def test_task_can_have_dependencies():
    task = Task(
        project_id="project-001",
        description="Write authentication tests",
        dependencies=("task-001", "task-002"),
    )

    assert len(task.dependencies) == 2
    assert "task-001" in task.dependencies