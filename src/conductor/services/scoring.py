from conductor.domain.enums import TaskPriority
from conductor.domain.task import Task
from conductor.services.priority_policy import effective_priority


PRIORITY_SCORE = {
    0: 1.0,  # HIGH
    1: 0.5,  # NORMAL
    2: 0.0,  # LOW
}

PRIORITY_WEIGHT = 0.5
IMPACT_WEIGHT = 0.5


def calculate_scores(
    tasks: list[Task],
    impact: dict[str, int],
) -> dict[str, float]:

    if not tasks:
        return {}

    max_impact = max(
        (impact.get(task.id, 0) for task in tasks),
        default=0,
    )

    scores = {}

    for task in tasks:
        priority_rank = effective_priority(task)

        priority_score = PRIORITY_SCORE[priority_rank]

        impact_score = (
            impact.get(task.id, 0) / max_impact
            if max_impact > 0
            else 0.0
        )

        scores[task.id] = (
            PRIORITY_WEIGHT * priority_score
            + IMPACT_WEIGHT * impact_score
        )

    return scores