# ADR-002: Separation of Task Planning and Retry Management

## Status
Accepted

## Context
In a multi-agent orchestration system, two distinct conditions arise when managing tasks:
1. **Dependency Resolution:** Determining which tasks are eligible to begin based on topological prerequisites and completed upstream dependencies.
2. **Failure & Retry Evaluation:** Determining what should happen when an agent execution session fails, crashes, times out, or produces failing tests.

If dependency calculation and retry logic are combined into a single scheduler or planning component:
- The eligibility calculation ceases to be a pure, deterministic function of the dependency graph.
- Retry policies (exponential backoff, maximum retry limits, failure categorization, cost thresholds) become tightly coupled with topological ordering.
- Testing graph algorithms requires mocking out timers, retry counters, and transient failure states.
- Race conditions emerge when concurrent agent sessions complete or fail simultaneously.

## Decision
We separate the responsibilities of planning, failure management, scheduling, and session execution into distinct architectural components:

1. **`Task Planner` (`src/conductor/services/task_planner.py`):**
   - A pure, side-effect-free function: `find_ready_tasks(tasks, completed_task_ids) -> list[Task]`.
   - Sole responsibility: Calculate which tasks in `PENDING` state have all their dependencies satisfied by `completed_task_ids`.
   - Never launches processes, never mutates task status, and never handles failure states.
2. **`Retry Manager` (Planned service):**
   - Sole responsibility: Evaluate failed execution sessions against configured retry policies (e.g., maximum attempts, failure class, backoff cooldown).
   - Decides whether a failed task should transition back to eligible for retry or transition permanently to `FAILED`.
3. **`Scheduler` (Planned service):**
   - Coordinates overall execution: queries the `Task Planner` for ready tasks, checks the `Retry Manager` for cooled-down retries, applies agent concurrency bounds, and initiates new sessions.
4. **`Session Manager` (Planned service):**
   - Manages the lifecycle of an individual agent execution attempt (`CREATED` -> `RUNNING` -> `SUCCEEDED` / `FAILED` / `INTERRUPTED`).

## Consequences

### Positive
- **Determinism:** `find_ready_tasks()` is a pure function that is straightforward to test and verify with zero side effects.
- **Pluggable Policies:** Retry behavior (linear backoff, exponential backoff, immediate retry on network errors, no retry on syntax errors) can be configured and updated without touching graph resolution logic.
- **Failure Isolation:** An execution failure in an agent process does not corrupt the dependency graph or immediately cascade into catastrophic failure for all dependent tasks.
- **Testability:** Unit tests for task dependency resolution do not need mock clocks, process handles, or retry state stores.

### Negative
- Requires a coordinating service (`Scheduler`) to synthesize the outputs of both the `Task Planner` and the `Retry Manager`.
- Additional domain state must be maintained to track retry attempts per task.

## Alternatives Considered
1. **Monolithic Scheduler Loop:** A single background loop that inspects tasks, checks dependency completion, inspects session exit codes, calculates retry delays, and spawns subprocesses. Rejected due to excessive coupling, non-deterministic state mutations, and extreme difficulty in unit testing.
2. **Task-Embedded Retry Logic:** Allowing `Task` entities to self-manage retry state and eligibility. Rejected because domain entities should remain pure data holders without operational behavior or execution side effects.
