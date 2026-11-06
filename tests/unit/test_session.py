from conductor.domain.sessions import Session
from conductor.domain.enums import SessionStatus


def test_session_creation():
    session = Session(
        project_id="project-001",
        task_id="task-001",
        agent_name="claude-code",
    )

    assert session.project_id == "project-001"
    assert session.task_id == "task-001"
    assert session.agent_name == "claude-code"
    assert session.status == SessionStatus.CREATED


def test_sessions_have_unique_ids():
    session_one = Session("project-001", "task-001", "claude-code")
    session_two = Session("project-001", "task-001", "claude-code")

    assert session_one.id != session_two.id