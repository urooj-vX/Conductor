# ADR-001: Separation of Project, Task, and Session

## Status
Accepted

## Context
When orchestrating autonomous AI coding agents across complex software repositories, Conductor must track where work happens, what work needs to be done, and who or what executed that work.

Initial simplistic designs often conflate the unit of work with its execution attempt—for example, treating a "Task" as an entity that directly contains execution process IDs, agent stdout/stderr logs, and process states. However, in autonomous software engineering:
1. An agent attempt may crash, time out, or produce failing code, requiring one or more retries of the same underlying work item.
2. A single repository contains many development tasks over time.
3. Multiple agents may execute distinct tasks concurrently on the same repository.
4. If task definitions are coupled directly to execution attempts, restarting a failed attempt either overwrites historical logs or mutates the specification of the work itself.

## Decision
We explicitly decouple the domain into three distinct entities with unambiguous 1:N relational boundaries:

1. **`Project`:** Represents the registered codebase and repository context (`name`, `repository_path`, `id`, `created_at`). Identity is decoupled from the filesystem path.
2. **`Task`:** Represents a declared unit of development work (`project_id`, `description`, `id`, `status: TaskStatus`, `dependencies: tuple[str, ...]`, `created_at`). A task specifies *what* needs to be achieved and its dependency prerequisites, not *how* or *by which process run* it is executed.
3. **`Session`:** Represents a single execution attempt of a task by a specific agent (`project_id`, `task_id`, `agent_name`, `id`, `status: SessionStatus`, `created_at`). A session models process execution, agent lifecycle states, and attempt outcomes.

A single `Project` owns multiple `Tasks`. A single `Task` can have zero, one, or multiple `Sessions` over its lifecycle (e.g. an initial failed session followed by a successful retry session).

## Consequences

### Positive
- **Clean Retries:** A task can fail a session and be scheduled for another attempt with a fresh `Session` without losing the logs or status of prior attempts.
- **Auditable History:** Complete execution history is preserved across all attempts.
- **Independent Lifecycles:** `TaskStatus` (`PENDING`, `READY`, `IN_PROGRESS`, `COMPLETED`, `FAILED`, `CANCELLED`) and `SessionStatus` (`CREATED`, `STARTING`, `RUNNING`, `WAITING_FOR_INPUT`, `BLOCKED`, `SUCCEEDED`, `FAILED`, `CANCELLED`, `INTERRUPTED`) evolve independently.
- **Relational Integrity:** Facilitates clean foreign-key relationships when persisted to relational databases (SQLite / SQLAlchemy).

### Negative
- Requires maintaining explicit foreign-key references (`project_id`, `task_id`) across dataclasses.
- Queries for the "current" state of a task's execution require querying or joining across both `Task` and `Session` entities.

## Alternatives Considered
1. **Combined Task and Session Entity:** Representing the agent attempt directly on the `Task` object. Rejected because failed attempts cannot be retried without overwriting previous execution metadata and timestamps.
2. **Path-as-Identity for Projects:** Using the repository's filesystem path as the primary key. Rejected because local repository paths can change (directory moves, server migrations) without altering the project's identity.
