from __future__ import annotations

import re
import sys
from pathlib import PurePosixPath


LOWER_KEBAB = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
LOWER_FILE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*(?:\.[a-z0-9]+(?:-[a-z0-9]+)*)*$")
PYTHON_FILE = re.compile(r"^(?:__init__|[a-z0-9]+(?:_[a-z0-9]+)*)(?:\.[a-z0-9]+)*\.py$")
MARKDOWN_STEM = re.compile(r"^(?:[a-z0-9]+(?:-[a-z0-9]+)*|[A-Z0-9]+(?:-[A-Z0-9]+)*)$")

ALLOWED_FILENAMES = {
    "Dockerfile",
    "README",
    "CODEOWNERS",
}


def normalize_hidden_name(name: str) -> str:
    if name.startswith(".") and len(name) > 1:
        return name[1:]
    return name


def valid_directory(name: str) -> bool:
    return bool(LOWER_KEBAB.fullmatch(normalize_hidden_name(name)))


def valid_file(name: str) -> bool:
    if name in ALLOWED_FILENAMES:
        return True

    normalized = normalize_hidden_name(name)

    if normalized.endswith(".md"):
        stem = normalized[:-3]
        return bool(MARKDOWN_STEM.fullmatch(stem))

    if normalized.endswith(".py"):
        return bool(PYTHON_FILE.fullmatch(normalized))

    return bool(LOWER_FILE.fullmatch(normalized))


def invalid_reason(path: str) -> str | None:
    parts = PurePosixPath(path).parts

    for directory in parts[:-1]:
        if not valid_directory(directory):
            return f"directory component `{directory}` must use lowercase kebab-case"

    filename = parts[-1]
    if not valid_file(filename):
        if filename.endswith(".md"):
            return f"Markdown file `{filename}` must use lowercase or uppercase kebab-case with `.md`"
        if filename.endswith(".py"):
            return f"Python file `{filename}` must use lowercase snake_case or be `__init__.py`"
        return f"file `{filename}` must use lowercase kebab-case; dots are allowed only for extensions"

    return None


def main() -> int:
    violations = [(path, reason) for path in sys.argv[1:] if (reason := invalid_reason(path))]

    if not violations:
        return 0

    print("Invalid path names found:")
    for path, reason in violations:
        print(f"- {path}: {reason}")

    print("\nRules:")
    print("- Directories: lowercase letters, numbers, and hyphens only.")
    print("- Markdown files: lowercase or uppercase stem, numbers and hyphens only, ending in `.md`.")
    print("- Python files: lowercase snake_case, or `__init__.py`.")
    print("- Other files: lowercase letters, numbers, hyphens, and extension dots only.")
    print("- Spaces are not allowed.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
