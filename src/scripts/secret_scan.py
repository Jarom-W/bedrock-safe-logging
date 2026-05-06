import re
import sys
from pathlib import Path

PATTERNS = {
    "aws_access_key_id": re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b"),
    "aws_secret_access_key_assignment": re.compile(
        r"(?i)\baws_secret_access_key\b\s*[:=]\s*['\"]?[A-Za-z0-9/+=]{20,}"
    ),
    "aws_session_token_assignment": re.compile(
        r"(?i)\baws_session_token\b\s*[:=]\s*['\"]?[A-Za-z0-9/+=._-]{20,}"
    ),
    "generic_secret_assignment": re.compile(
        r"(?i)\b(api[_-]?key|secret|token|password)\b\s*[:=]\s*['\"]?[^\s\"',;]{8,}"
    ),
}

SKIP_DIRS = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    ".pytest_cache",
}

SKIP_FILES = {
    ".env",  # local only; should be gitignored
}

def should_skip(path: Path) -> bool:
    return any(part in SKIP_DIRS for part in path.parts) or path.name in SKIP_FILES

def main() -> int:
    findings = []

    for path in Path(".").rglob("*"):
        if not path.is_file() or should_skip(path):
            continue #Skip non-files or specified skipping fiels/dirs
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue

        for name, pattern in PATTERNS.items():
            for match in pattern.finditer(text):
                line_no = text.count("\n", 0, match.start()) + 1
                findings.append((str(path), line_no, name))

    if findings:
        print("Potential secrets found:")
        for file, line, name in findings:
            print(f" {file}:{line} matched {name}")
        return 1

    print("No secret patterns found")
    return 0
if __name__ == "__main__":
    sys.exit(main())
