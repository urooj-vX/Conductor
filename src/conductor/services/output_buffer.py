from collections import deque


class OutputBuffer:

    def __init__(self, max_lines: int = 100):
        if max_lines <= 0:
            raise ValueError("max_lines must be positive")

        self._lines = deque(maxlen=max_lines)

    def append(self, stream: str, line: str) -> None:
        self._lines.append({
            "stream": stream,
            "content": line,
        })

    def get_recent(self) -> list[dict[str, str]]:
        return list(self._lines)

    def __len__(self) -> int:
        return len(self._lines)