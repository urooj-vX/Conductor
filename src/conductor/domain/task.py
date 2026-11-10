from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import uuid4

from conductor.domain.enums import TaskStatus

from conductor.domain.enums import TaskStatus, TaskPriority

@dataclass
class Task:
    project_id: str
    description: str

    id: str = field(default_factory=lambda: str(uuid4()))

    status: TaskStatus = TaskStatus.PENDING

    dependencies: tuple[str, ...] = ()

    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    priority: TaskPriority = TaskPriority.NORMAL