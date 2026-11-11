from conductor.domain.task import Task
from conductor.services.impact_analyzer import calculate_downstream_impact


def test_calculates_transitive_downstream_impact():
    tasks = [
        Task("P1", "Task A", id="A"),
        Task("P1", "Task B", id="B", dependencies=("A",)),
        Task("P1", "Task C", id="C", dependencies=("B",)),
    ]

    impact = calculate_downstream_impact(tasks)

    assert impact["A"] == 2
    assert impact["B"] == 1
    assert impact["C"] == 0


def test_counts_shared_dependents_only_once():
    tasks = [
        Task("P1", "Task A", id="A"),
        Task("P1", "Task B", id="B", dependencies=("A",)),
        Task("P1", "Task C", id="C", dependencies=("A",)),
        Task(
            "P1",
            "Task D",
            id="D",
            dependencies=("B", "C"),
        ),
    ]

    impact = calculate_downstream_impact(tasks)

    assert impact["A"] == 3