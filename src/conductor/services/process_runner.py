
import asyncio
from collections.abc import Callable
from dataclasses import dataclass


@dataclass(frozen=True)
class ProcessResult:
    exit_code: int
    stdout: str
    stderr: str


async def run_process(*command: str) -> ProcessResult:
    process = await asyncio.create_subprocess_exec(
        *command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    stdout, stderr = await process.communicate()

    return ProcessResult(
        exit_code=process.returncode,
        stdout=stdout.decode(errors="replace"),
        stderr=stderr.decode(errors="replace"),
    )


async def run_process_streaming(
    *command: str,
    on_output: Callable[[str, str], None],
) -> ProcessResult:

    process = await asyncio.create_subprocess_exec(
        *command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    assert process.stdout is not None
    assert process.stderr is not None

    stdout_chunks: list[str] = []
    stderr_chunks: list[str] = []

    async def read_stream(
        stream: asyncio.StreamReader,
        stream_name: str,
        output_chunks: list[str],
    ) -> None:

        while chunk := await stream.read(1024):
            text = chunk.decode(errors="replace")

            output_chunks.append(text)
            on_output(stream_name, text)

    try:
        await asyncio.gather(
            read_stream(process.stdout, "stdout", stdout_chunks),
            read_stream(process.stderr, "stderr", stderr_chunks),
            process.wait(),
        )

    except BaseException:
        if process.returncode is None:
            process.terminate()
            await process.wait()
        raise

    return ProcessResult(
        exit_code=process.returncode,
        stdout="".join(stdout_chunks),
        stderr="".join(stderr_chunks),
    )
