import sys
import pytest

from conductor.services.process_runner import run_process


@pytest.mark.asyncio
async def test_successful_process():
    result = await run_process(
        sys.executable,
        "-c",
        "print('Hello from Conductor')",
    )

    assert result.exit_code == 0
    assert "Hello from Conductor" in result.stdout


@pytest.mark.asyncio
async def test_failed_process():
    result = await run_process(
        sys.executable,
        "-c",
        "import sys; sys.exit(1)",
    )

    assert result.exit_code == 1