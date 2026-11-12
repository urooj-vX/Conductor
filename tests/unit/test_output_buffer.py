import pytest

from conductor.services.output_buffer import OutputBuffer


def test_buffer_keeps_latest_lines():
    buffer = OutputBuffer(max_lines=3)

    buffer.append("stdout", "Line 1")
    buffer.append("stdout", "Line 2")
    buffer.append("stdout", "Line 3")
    buffer.append("stdout", "Line 4")

    result = buffer.get_recent()

    assert len(result) == 3
    assert [line["content"] for line in result] == [
        "Line 2",
        "Line 3",
        "Line 4",
    ]


def test_buffer_preserves_output_stream():
    buffer = OutputBuffer()

    buffer.append("stdout", "Agent started")
    buffer.append("stderr", "Warning detected")

    result = buffer.get_recent()

    assert result[0]["stream"] == "stdout"
    assert result[1]["stream"] == "stderr"


def test_buffer_rejects_zero_capacity():
    with pytest.raises(ValueError):
        OutputBuffer(max_lines=0)


def test_buffer_does_not_exceed_capacity():
    buffer = OutputBuffer(max_lines=100)

    for i in range(10_000):
        buffer.append("stdout", f"Line {i}")

    assert len(buffer) == 100
    assert buffer.get_recent()[-1]["content"] == "Line 9999"