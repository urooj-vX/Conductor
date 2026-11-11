from conductor.domain.task import Task
from conductor.domain.enums import TaskPriority
from conductor.services.scoring import calculate_scores


def test_priority_and_impact_have_equal_weight():
    task_a = Task(
        "P1", "Low priority", id="A",
        priority=TaskPriority.LOW,
    )

    task_b = Task(
        "P1", "High priority", id="B",
        priority=TaskPriority.HIGH,
    )

    scores = calculate_scores(
        [task_a, task_b],
        {"A": 2, "B": 0},
    )

    assert scores["A"] == 0.5
    assert scores["B"] == 0.5


def test_impact_is_normalized():
    task = Task("P1", "Task A", id="A")

    scores = calculate_scores([task], {"A": 5})

    assert 0.0 <= scores["A"] <= 1.0


def test_empty_task_list_returns_empty_scores():
    assert calculate_scores([], {}) == {}