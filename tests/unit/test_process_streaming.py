import sys
import pytest

from conductor.services.process_runner import run_process_streaming


@pytest.mark.asyncio
async def test_streams_stdout_and_stderr():
    received = []

    def capture_output(stream, text):
        received.append((stream, text))

    result = await run_process_streaming(
        sys.executable,
        "-c",
        "import sys; "
        "print('Agent started', flush=True); "
        "print('Test warning', file=sys.stderr, flush=True)",
        on_output=capture_output,
    )

    assert result.exit_code == 0
    assert "Agent started" in result.stdout
    assert "Test warning" in result.stderr

    assert any(
        stream == "stdout" and "Agent started" in text
        for stream, text in received
    )

    assert any(
        stream == "stderr" and "Test warning" in text
        for stream, text in received
    )