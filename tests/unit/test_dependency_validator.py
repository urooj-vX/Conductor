import pytest

from conductor.domain.task import Task
from conductor.services.dependency_validator import validate_dependencies


def test_valid_dependencies():
    task_a = Task("P1", "Create database", id="A")
    task_b = Task(
        "P1",
        "Implement API",
        id="B",
        dependencies=("A",),
    )

    validate_dependencies([task_a, task_b])


def test_rejects_self_dependency():
    task = Task(
        "P1",
        "Create database",
        id="A",
        dependencies=("A",),
    )

    with pytest.raises(ValueError, match="cannot depend on itself"):
        validate_dependencies([task])


def test_rejects_missing_dependency():
    task = Task(
        "P1",
        "Implement API",
        id="B",
        dependencies=("UNKNOWN",),
    )

    with pytest.raises(ValueError, match="does not exist"):
        validate_dependencies([task])

def test_rejects_circular_dependencies():
    task_a = Task("P1", "Task A", id="A", dependencies=("B",))
    task_b = Task("P1", "Task B", id="B", dependencies=("C",))
    task_c = Task("P1", "Task C", id="C", dependencies=("A",))

    with pytest.raises(ValueError, match="Circular dependency"):
        validate_dependencies([task_a, task_b, task_c])


def test_accepts_valid_dependency_chain():
    task_a = Task("P1", "Task A", id="A")
    task_b = Task("P1", "Task B", id="B", dependencies=("A",))
    task_c = Task("P1", "Task C", id="C", dependencies=("B",))

    validate_dependencies([task_a, task_b, task_c])

def test_detects_cycle_in_disconnected_component():
    task_a = Task("P1", "Task A", id="A")
    task_b = Task("P1", "Task B", id="B")

    task_c = Task("P1", "Task C", id="C", dependencies=("D",))
    task_d = Task("P1", "Task D", id="D", dependencies=("C",))

    with pytest.raises(ValueError, match="Circular dependency"):
        validate_dependencies([task_a, task_b, task_c, task_d])

def test_accepts_parallel_dependencies():
    task_a = Task("P1", "Task A", id="A")
    task_b = Task("P1", "Task B", id="B", dependencies=("A",))
    task_c = Task("P1", "Task C", id="C", dependencies=("A",))
    task_d = Task(
        "P1",
        "Task D",
        id="D",
        dependencies=("B", "C"),
    )

    validate_dependencies([task_a, task_b, task_c, task_d])