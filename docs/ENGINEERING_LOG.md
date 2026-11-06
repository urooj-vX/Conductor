# Conductor — Engineering Log

This engineering log documents the day-to-day development journey, technical decisions, debugging incidents, and lessons learned while building **Conductor**—a local-first multi-agent coding orchestration platform.

For architectural decisions, see also the [Architecture Decision Records](adr/).
For high-level project documentation, see the [README](../README.md).

---

## Daily Engineering Logs (Days 1–5)

### Day 01 — Project foundation

**Objective**
Establish a reproducible, modern Python package foundation for Conductor using `uv`, configure the source layout, and initialize version control.

**Implementation**
- Initialized the project environment targeting Python `>=3.14` using the `uv` toolchain.
- Generated `pyproject.toml` specifying build backend `uv_build` and package metadata.
- Configured dependencies: `fastapi>=0.162.0`, `pydantic-settings>=2.16.2`, and `uvicorn[standard]>=0.54.0`.
- Configured a console script entry point in `pyproject.toml`: `conductor = "conductor:main"`.
- Established a `src/` layout with `src/conductor/__init__.py` containing a foundational `main()` function printing `"Hello from conductor!"`.
- Generated deterministic dependency lockfile `uv.lock`.
- Initialized Git repository, pinned `.python-version` (3.14), and recorded initial commit (`1be43ce`).
- Aligned package layout and top-level namespace under `src/conductor/` (`fc8651e`).

**Technical concepts learned**
- **`src` Layout Benefits:** Using a `src/` directory layout (`src/conductor/`) rather than putting the package at the repository root prevents Python from importing local uninstalled modules during test runs, forcing tests to execute against properly installed and resolved package distributions.
- **`uv` Package Management:** `uv` provides sub-millisecond dependency resolution, integrated virtual environment management, and cross-platform lockfile generation (`uv.lock`) replacing traditional fragmented tools (`pip`, `virtualenv`, `poetry`).
- **Namespace Packaging & Entry Points:** Configuring `[project.scripts]` in `pyproject.toml` binds console commands directly to package callables when installed in editable or virtual environments.

**Engineering problems encountered**
- Initial module layout required alignment to ensure that domain submodules (such as `conductor.domain.enums`) could be imported consistently both internally and by external consumers without import path ambiguity.

**How we solved them**
- Explicitly organized all modules under the top-level `conductor` namespace in `src/conductor/` and verified imports by executing the package entry point.

**Architecture decisions**
- Use `conductor` as the single, consistent Python package namespace across the entire codebase.
- Enforce the `src/` directory layout for all application code.

**Testing and verification**
- Verified package entry point via terminal execution:
  ```bash
  uv run conductor
  ```
  Output confirmed: `Hello from conductor!`.

**Key takeaway**
Adopting a clean `src` layout and a deterministic lockfile on Day 1 eliminates downstream import ambiguities and environment drift before any domain logic is written.

---

### Day 02 — Session domain model

**Objective**
Model the agent execution session entity representing an individual execution attempt of a development task by an AI coding agent.

**Implementation**
- Created `SessionStatus` enum in `src/conductor/domain/enums.py` containing states:
  - `CREATED`, `STARTING`, `RUNNING`, `WAITING_FOR_INPUT`, `BLOCKED`, `SUCCEEDED`, `FAILED`, `CANCELLED`, `INTERRUPTED`.
- Created `Session` dataclass in `src/conductor/domain/sessions.py` with fields:
  - `project_id: str`
  - `task_id: str`
  - `agent_name: str`
  - `id: str` (UUID4 string via `default_factory`)
  - `status: SessionStatus` (default: `SessionStatus.CREATED`)
  - `created_at: datetime` (timezone-aware UTC via `datetime.now(timezone.utc)`)
- Added `pytest>=9.2.0` and `pytest-asyncio>=1.4.1.post1` to `[dependency-groups] dev` in `pyproject.toml` and updated `uv.lock`.
- Created unit tests in `tests/unit/test_session.py` covering session instantiation and UUID uniqueness.
- Committed changes (`3b411f1`).

**Technical concepts learned**
- **Dataclass Field Default Factories:** In Python dataclasses, mutable defaults or dynamic generation (like `uuid4()` and timestamps) must use `field(default_factory=...)` to ensure each instance receives a distinct value evaluated at instantiation time.
- **Timezone-Aware UTC Timestamps:** Naive datetimes (`datetime.now()`) cause silent comparison bugs across different host timezones; using `datetime.now(timezone.utc)` guarantees deterministic timestamps.
- **Process vs. Session Lifecycle:** An agent session is an abstraction over an external process. The session's state must account for unexpected supervisor or system events.

**Engineering problems encountered**
- Invoking `pytest` directly from the shell failed or generated unexpected interpreter warnings because the system resolved a global Anaconda Python interpreter (`/opt/anaconda3/...`) rather than the project's virtual environment. The global environment lacked the project's dependencies and could not resolve `conductor`.

**How we solved them**
- Added `pytest` and `pytest-asyncio` as explicit development dependencies in `pyproject.toml` managed by `uv`.
- Enforced invoking tests through `uv run python -m pytest`, which guarantees execution inside the managed virtual environment with `src/` on the module search path.

**Architecture decisions**
- **Distinguish `FAILED` from `INTERRUPTED`:** An agent session that fails due to bad code, command syntax, or failing tests is marked `FAILED`. If the Conductor host process crashes, is killed, or restarts while an agent is running, the session cannot be assumed to have failed its objective. Marking it `INTERRUPTED` allows recovery mechanisms to reconcile running processes upon restart.
- **String UUID Identifiers:** Use UUID4 strings for entity identity to enable distributed generation and database independence without integer autoincrement contention.

**Testing and verification**
- Ran `uv run python -m pytest tests/unit/test_session.py`:
  - `test_session_creation`: Verified fields and default `CREATED` status.
  - `test_sessions_have_unique_ids`: Verified distinct UUID generation across consecutive instances.
  - 2 passed.

**Key takeaway**
A host crash is not an agent failure; modeling `INTERRUPTED` as a first-class lifecycle state is essential for building crash-resilient process orchestration.

---

### Day 03 — Project domain model

**Objective**
Model the registered software repository entity (`Project`) in Conductor.

**Implementation**
- Created `Project` dataclass in `src/conductor/domain/project.py` with fields:
  - `name: str`
  - `repository_path: Path` (using `pathlib.Path`)
  - `id: str` (UUID4 string via `default_factory`)
  - `created_at: datetime` (timezone-aware UTC via `default_factory`)
- Committed in `54ec1c8`.

**Technical concepts learned**
- **`pathlib.Path` over Raw Strings:** Modeling filesystem paths as `pathlib.Path` objects provides cross-platform path resolution, validation, and traversal methods while enforcing type safety.
- **Decoupling Entity Identity from Storage Location:** Treating filesystem paths as mutable attributes rather than primary keys ensures that local repository reorganization does not invalidate existing project IDs.

**Engineering problems encountered**
- During initial commit of the project entity, `tests/unit/test_project.py` was committed with a duplicate definition of the `Project` dataclass rather than test functions (`def test_...`). As a result, pytest collected 0 tests from `test_project.py`.

**How we solved them**
- Identified the gap during test suite verification. Preserved the integrity of the existing repository code without making out-of-scope edits; logged the need for comprehensive Project unit test assertions in the test suite backlog.

**Architecture decisions**
- **Independent Project Identity:** A Project's identity (`id`) is a UUID, completely independent of its filesystem `repository_path`. If a repository is moved on disk, its identity and associated task history remain intact.
- **Repository Uniqueness Policy:** Conductor's architectural policy is one registered `Project` per underlying repository path. Enforcement of this uniqueness constraint is deferred to the planned persistence/API layer.
- **Git Worktree Isolation:** Rather than executing agents directly inside the main `repository_path`, Conductor plans to use Git worktrees branched from this repository for agent isolation.

**Testing and verification**
- Verified `Project` instantiation in Python 3.14 REPL using `pathlib.Path("/tmp/repo")`.
- Verified pytest run; noted that `tests/unit/test_project.py` contains the entity definition without test functions, so 0 test items were collected from this specific file.

**Key takeaway**
Domain entities should never use mutable filesystem locations as primary keys.

---

### Day 04 — Task domain model

**Objective**
Model discrete units of development work (`Task`), their lifecycle states, and dependency relationships.

**Implementation**
- Added `TaskStatus` enum to `src/conductor/domain/enums.py`:
  - `PENDING`: Initial state, waiting for dependencies or scheduling.
  - `READY`: All dependencies satisfied, eligible for scheduling.
  - `IN_PROGRESS`: Currently being executed by an agent in an active session.
  - `COMPLETED`: Work verified and finished successfully.
  - `FAILED`: Task failed execution and exhausted retry policies.
  - `CANCELLED`: Manually or cascade cancelled.
- Created `Task` dataclass in `src/conductor/domain/task.py` with fields:
  - `project_id: str`
  - `description: str`
  - `id: str` (UUID4 string via `default_factory`)
  - `status: TaskStatus` (default: `TaskStatus.PENDING`)
  - `dependencies: tuple[str, ...]` (default: empty tuple `()`)
  - `created_at: datetime` (timezone-aware UTC via `default_factory`)
- Added unit tests in `tests/unit/test_task.py` verifying instantiation, defaults, uniqueness, and dependency assignment.
- Committed in `49905e2`.

**Technical concepts learned**
- **Immutable Dependency Tuples:** Using `tuple[str, ...]` instead of `list[str]` for dependencies prevents accidental in-place mutation of a task's dependency graph after definition.
- **Separation of Task and Session Lifecycles:** A task represents *what* needs to be done; a session represents *an attempt* to do it. A task can experience multiple sessions across failures and retries before reaching `COMPLETED`.

**Engineering problems encountered**
- Determining whether task dependencies should be represented as full object references (`tuple[Task, ...]`) or entity IDs (`tuple[str, ...]`). Storing full object references leads to circular references, serialization difficulty, and challenges when persisting entities in relational tables.

**How we solved them**
- Represented dependencies strictly by string identifiers (`tuple[str, ...]`), enabling clean foreign-key mapping, trivial serialization, and decoupling task instantiation order.

**Architecture decisions**
- **Project, Task, and Session are distinct entities:** (Documented in [ADR-001](adr/0001-separation-of-project-task-and-session.md)).
- **A task owns multiple execution sessions:** If an agent session fails, the task returns to an eligible state for retry without mutating its original requirements.
- **Dependencies are immutable:** Defined at task creation time as a tuple of prerequisite task IDs.

**Testing and verification**
- Ran `uv run python -m pytest tests/unit/test_task.py`:
  - `test_task_creation`: Verified field assignment, default `PENDING` status, and empty tuple dependencies.
  - `test_tasks_have_unique_ids`: Verified distinct UUID generation across task instances.
  - `test_task_can_have_dependencies`: Verified dependency tuple assignment and membership.
  - 3 passed.

**Key takeaway**
Decoupling the unit of work (`Task`) from the execution attempt (`Session`) is the foundational prerequisite for clean failure recovery and retries.

---

### Day 05 — Dependency-aware Task Planner

**Objective**
Implement a pure, dependency-aware task planner that calculates which tasks are eligible for execution based on upstream task completion.

**Implementation**
- Created `find_ready_tasks(tasks: list[Task], completed_task_ids: set[str]) -> list[Task]` in `src/conductor/services/task_planner.py`.
- Filter criteria:
  1. `task.status == TaskStatus.PENDING`
  2. `task.id not in completed_task_ids`
  3. `all(dependency_id in completed_task_ids for dependency_id in task.dependencies)`
- Created unit tests in `tests/unit/test_task_planner.py` modeling a multi-stage dependency graph:
  - Task A: "Create database schema" (no dependencies)
  - Task B: "Implement API" (depends on A)
  - Task C: "Write API tests" (depends on B)
  - Task D: "Update documentation" (depends on A)
- Fixed bug where completed tasks were returned as ready (`1c5a98b`).

**Execution Example Walkthrough**
Given the graph above:
1. **Initial State (`completed_task_ids = set()`):**
   - Only Task A has all dependencies satisfied (`all([]) == True`).
   - `find_ready_tasks` returns `[Task A]`.
2. **After A Completes (`completed_task_ids = {"A"}`):**
   - Task B (depends on A) and Task D (depends on A) both have their dependencies satisfied.
   - `find_ready_tasks` returns `[Task B, Task D]`. These can be scheduled concurrently in parallel workspaces.
3. **After B Completes (`completed_task_ids = {"A", "B"}`):**
   - Task C (depends on B) becomes eligible, alongside Task D (if D is still pending).
   - `find_ready_tasks` returns `[Task C, Task D]`.

**Technical concepts learned**
- **Vacuous Truth in Boolean Logic:** In Python, `all([])` evaluates to `True`. If a task has no dependencies (`dependencies = ()`), `all(dep in completed for dep in task.dependencies)` is immediately `True`.
- **Pure Functional Planning:** Designing the planner as a pure function `(tasks, completed_ids) -> ready_tasks` eliminates race conditions, simplifies testing, and decouples scheduling from state mutation.

**Engineering problems encountered**
- **The Vacuous Truth Ready Queue Bug:** When `find_ready_tasks` evaluated tasks, completed tasks that had no dependencies satisfied `all([]) == True`. If task status was not checked or if a completed task was still passed in the list, the planner erroneously included the completed task in the ready queue!

**How we solved them**
- Added explicit guard conditions:
  ```python
  task.status == TaskStatus.PENDING and task.id not in completed_task_ids
  ```
  This guarantees that only pending, uncompleted tasks can ever be marked ready.

**Architecture decisions**
- **Task Planner only calculates eligibility:** The planner does not execute tasks, spawn agents, mutate database records, or manage retries (documented in [ADR-002](adr/0002-separation-of-task-planning-and-retry-management.md)).
- **Separation of Planning and Execution:** The Scheduler and Retry Manager are separate components. The Task Planner remains a pure mathematical evaluator of the task DAG.

**Testing and verification**
- Ran `uv run python -m pytest tests/unit/test_task_planner.py`:
  - `test_only_independent_task_is_ready_initially`: Passed.
  - `test_parallel_tasks_become_ready_after_a`: Passed.
  - `test_c_becomes_ready_after_b`: Passed.
  - 3 passed.
- Entire test suite: 8 passed across all unit test files.

**Key takeaway**
Mathematical edge cases like vacuous truth (`all([]) == True`) will cause subtle scheduling bugs unless guarded by explicit domain status checks.

---

## Consolidated Architecture Decisions

The following foundational architecture decisions have been established during Days 1–5:

1. **Project, Task, and Session are separate entities:**
   Decouples the repository context, the unit of work, and the execution attempt, enabling retries and auditable history.
2. **Project IDs are independent of repository paths:**
   Moving or renaming a local repository does not invalidate existing project IDs or historical execution logs.
3. **Single registration per repository policy:**
   Duplicate registration of the same underlying repository path should eventually be rejected by the persistence layer.
4. **Git worktrees for workspace isolation:**
   Agents will execute in isolated Git worktrees rather than modifying the main working copy directly, preventing merge conflicts and dirty states.
5. **`FAILED` and `INTERRUPTED` represent different conditions:**
   Process crashes or Conductor restarts result in `INTERRUPTED` sessions, allowing startup recovery routines to reconcile state rather than treating crashes as code failures.
6. **Task dependencies determine execution eligibility:**
   Tasks are executed according to a directed acyclic graph (DAG); no dependent task can run until all prerequisite tasks are completed.
7. **Task Planner and Retry Manager must remain separate:**
   The Task Planner is a pure function that resolves DAG dependencies. The Retry Manager handles failure policies, backoff timers, and retry limits.
8. **Decoupled Scheduler coordination:**
   The Retry Manager evaluates retry eligibility; the Scheduler coordinates subsequent execution and agent worker dispatch.
9. **Failure isolation across dependent tasks:**
   A failed upstream task should not automatically cause all dependent tasks to permanently fail; failure policies and retries can recover the upstream task.
10. **Small, testable components over premature distributed infrastructure:**
    Prioritize pure functions, clean domain models, and fast unit tests before introducing distributed message brokers or heavy external databases.

---

## Future Engineering Log Templates (Days 6–30)

The following entries are reserved templates for upcoming development milestones. They will be completed as implementation progresses.

### Day 06 — [Milestone]

**Objective:**

**Implementation:**

**Technical concepts learned:**

**Engineering problems encountered:**

**Root cause:**

**How we solved them:**

**Architecture decisions:**

**Tests and verification:**

**Key takeaway:**

---

### Day 07 — [Milestone]

**Objective:**

**Implementation:**

**Technical concepts learned:**

**Engineering problems encountered:**

**Root cause:**

**How we solved them:**

**Architecture decisions:**

**Tests and verification:**

**Key takeaway:**

---

### Day 08 — [Milestone]

**Objective:**

**Implementation:**

**Technical concepts learned:**

**Engineering problems encountered:**

**Root cause:**

**How we solved them:**

**Architecture decisions:**

**Tests and verification:**

**Key takeaway:**

---

### Day 09 — [Milestone]

**Objective:**

**Implementation:**

**Technical concepts learned:**

**Engineering problems encountered:**

**Root cause:**

**How we solved them:**

**Architecture decisions:**

**Tests and verification:**

**Key takeaway:**

---

### Day 10 — [Milestone]

**Objective:**

**Implementation:**

**Technical concepts learned:**

**Engineering problems encountered:**

**Root cause:**

**How we solved them:**

**Architecture decisions:**

**Tests and verification:**

**Key takeaway:**

---

### Day 11 — [Milestone]

**Objective:**

**Implementation:**

**Technical concepts learned:**

**Engineering problems encountered:**

**Root cause:**

**How we solved them:**

**Architecture decisions:**

**Tests and verification:**

**Key takeaway:**

---

### Day 12 — [Milestone]

**Objective:**

**Implementation:**

**Technical concepts learned:**

**Engineering problems encountered:**

**Root cause:**

**How we solved them:**

**Architecture decisions:**

**Tests and verification:**

**Key takeaway:**

---

### Day 13 — [Milestone]

**Objective:**

**Implementation:**

**Technical concepts learned:**

**Engineering problems encountered:**

**Root cause:**

**How we solved them:**

**Architecture decisions:**

**Tests and verification:**

**Key takeaway:**

---

### Day 14 — [Milestone]

**Objective:**

**Implementation:**

**Technical concepts learned:**

**Engineering problems encountered:**

**Root cause:**

**How we solved them:**

**Architecture decisions:**

**Tests and verification:**

**Key takeaway:**

---

### Day 15 — [Milestone]

**Objective:**

**Implementation:**

**Technical concepts learned:**

**Engineering problems encountered:**

**Root cause:**

**How we solved them:**

**Architecture decisions:**

**Tests and verification:**

**Key takeaway:**

---

### Day 16 — [Milestone]

**Objective:**

**Implementation:**

**Technical concepts learned:**

**Engineering problems encountered:**

**Root cause:**

**How we solved them:**

**Architecture decisions:**

**Tests and verification:**

**Key takeaway:**

---

### Day 17 — [Milestone]

**Objective:**

**Implementation:**

**Technical concepts learned:**

**Engineering problems encountered:**

**Root cause:**

**How we solved them:**

**Architecture decisions:**

**Tests and verification:**

**Key takeaway:**

---

### Day 18 — [Milestone]

**Objective:**

**Implementation:**

**Technical concepts learned:**

**Engineering problems encountered:**

**Root cause:**

**How we solved them:**

**Architecture decisions:**

**Tests and verification:**

**Key takeaway:**

---

### Day 19 — [Milestone]

**Objective:**

**Implementation:**

**Technical concepts learned:**

**Engineering problems encountered:**

**Root cause:**

**How we solved them:**

**Architecture decisions:**

**Tests and verification:**

**Key takeaway:**

---

### Day 20 — [Milestone]

**Objective:**

**Implementation:**

**Technical concepts learned:**

**Engineering problems encountered:**

**Root cause:**

**How we solved them:**

**Architecture decisions:**

**Tests and verification:**

**Key takeaway:**

---

### Day 21 — [Milestone]

**Objective:**

**Implementation:**

**Technical concepts learned:**

**Engineering problems encountered:**

**Root cause:**

**How we solved them:**

**Architecture decisions:**

**Tests and verification:**

**Key takeaway:**

---

### Day 22 — [Milestone]

**Objective:**

**Implementation:**

**Technical concepts learned:**

**Engineering problems encountered:**

**Root cause:**

**How we solved them:**

**Architecture decisions:**

**Tests and verification:**

**Key takeaway:**

---

### Day 23 — [Milestone]

**Objective:**

**Implementation:**

**Technical concepts learned:**

**Engineering problems encountered:**

**Root cause:**

**How we solved them:**

**Architecture decisions:**

**Tests and verification:**

**Key takeaway:**

---

### Day 24 — [Milestone]

**Objective:**

**Implementation:**

**Technical concepts learned:**

**Engineering problems encountered:**

**Root cause:**

**How we solved them:**

**Architecture decisions:**

**Tests and verification:**

**Key takeaway:**

---

### Day 25 — [Milestone]

**Objective:**

**Implementation:**

**Technical concepts learned:**

**Engineering problems encountered:**

**Root cause:**

**How we solved them:**

**Architecture decisions:**

**Tests and verification:**

**Key takeaway:**

---

### Day 26 — [Milestone]

**Objective:**

**Implementation:**

**Technical concepts learned:**

**Engineering problems encountered:**

**Root cause:**

**How we solved them:**

**Architecture decisions:**

**Tests and verification:**

**Key takeaway:**

---

### Day 27 — [Milestone]

**Objective:**

**Implementation:**

**Technical concepts learned:**

**Engineering problems encountered:**

**Root cause:**

**How we solved them:**

**Architecture decisions:**

**Tests and verification:**

**Key takeaway:**

---

### Day 28 — [Milestone]

**Objective:**

**Implementation:**

**Technical concepts learned:**

**Engineering problems encountered:**

**Root cause:**

**How we solved them:**

**Architecture decisions:**

**Tests and verification:**

**Key takeaway:**

---

### Day 29 — [Milestone]

**Objective:**

**Implementation:**

**Technical concepts learned:**

**Engineering problems encountered:**

**Root cause:**

**How we solved them:**

**Architecture decisions:**

**Tests and verification:**

**Key takeaway:**

---

### Day 30 — [Milestone]

**Objective:**

**Implementation:**

**Technical concepts learned:**

**Engineering problems encountered:**

**Root cause:**

**How we solved them:**

**Architecture decisions:**

**Tests and verification:**

**Key takeaway:**
