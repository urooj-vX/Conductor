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