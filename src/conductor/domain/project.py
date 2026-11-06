from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4


@dataclass
class Project:
    name: str
    repository_path: Path

    id: str = field(default_factory=lambda: str(uuid4()))

    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )