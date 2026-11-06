from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import uuid4

from conductor.domain.enums import SessionStatus


@dataclass
class Session:
    project_id: str
    task_id: str
    agent_name: str

    id: str = field(default_factory=lambda: str(uuid4()))

    status: SessionStatus = SessionStatus.CREATED

    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )