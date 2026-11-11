from datetime import datetime, timedelta, timezone

import pytest

from conductor.services.activity_monitor import (
    ProcessActivity,
    get_process_activity,
)


def test_process_is_active_when_output_is_recent():
    now = datetime.now(timezone.utc)

    result = get_process_activity(
        last_output_at=now - timedelta(seconds=10),
        now=now,
        idle_threshold_seconds=60,
    )

    assert result == ProcessActivity.ACTIVE


def test_process_is_quiet_when_output_stops():
    now = datetime.now(timezone.utc)

    result = get_process_activity(
        last_output_at=now - timedelta(seconds=90),
        now=now,
        idle_threshold_seconds=60,
    )

    assert result == ProcessActivity.QUIET


def test_process_without_output_is_quiet():
    now = datetime.now(timezone.utc)

    result = get_process_activity(
        last_output_at=None,
        now=now,
        idle_threshold_seconds=60,
    )

    assert result == ProcessActivity.QUIET


def test_exited_process_is_not_quiet():
    now = datetime.now(timezone.utc)

    result = get_process_activity(
        last_output_at=None,
        now=now,
        idle_threshold_seconds=60,
        is_running=False,
    )

    assert result == ProcessActivity.EXITED


def test_rejects_naive_timestamps():
    now = datetime.now()

    with pytest.raises(ValueError, match="timezone-aware"):
        get_process_activity(
            last_output_at=now,
            now=now,
            idle_threshold_seconds=60,
        )