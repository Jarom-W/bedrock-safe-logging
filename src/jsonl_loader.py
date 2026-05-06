import json
from pathlib import Path
from typing import Any

def load_jsonl(path: str) -> list[dict[str, Any]]:
    """
    Load JSONL from file into memory. 
    """

    events: list[dict[str, Any]] = []
    file_path = Path(path)

    if not file_path.exists():
        raise FileNotFoundError(f"Replay JSONL file not found: {path}")
    with file_path.open("r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            line = line.strip()

            if not line:
                continue

            try:
                events.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSONL at {path}:{line_number}") from exc

    return events
