#!/usr/bin/env python3
"""Validate local and CI quality-gate wiring for this book.

The repository has multiple independent checks (navigation coverage, security
audit, markdown lint/link checks, spellcheck, and Jekyll/pytest based checks).
This script keeps the lightweight npm/CI entry points aligned so dependency
security and documented contributor commands do not drift silently.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


class CheckError(ValueError):
    pass


def load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise CheckError(f"{path}: expected a JSON object")
    return data


def require_contains(text: str, needle: str, *, source: str, errors: list[str]) -> None:
    if needle not in text:
        errors.append(f"{source}: must contain {needle!r}")


def validate_package(package: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    scripts = package.get("scripts")
    if not isinstance(scripts, dict):
        return ["package.json: scripts must be an object"]

    expected_scripts = {
        "check:quality": "python3 scripts/check_quality_gates.py",
        "check:metadata": "python3 scripts/check_publication_metadata.py",
        "check:security": "npm audit --omit=optional",
        "check:navigation": "python3 scripts/check_navigation_coverage.py",
        "check:effort": "python3 scripts/check_effort_metadata.py",
    }
    for name, expected in expected_scripts.items():
        actual = scripts.get(name)
        if actual != expected:
            errors.append(f"package.json: scripts.{name} must be {expected!r} (actual={actual!r})")

    test_script = scripts.get("test")
    if not isinstance(test_script, str):
        errors.append("package.json: scripts.test must be a string")
    else:
        for command in (
            "npm run check:quality",
            "npm run check:metadata",
            "npm run check:effort",
            "npm run check:navigation",
            "npm run check:security",
            "npm run lint",
            "npm run check-links",
        ):
            require_contains(test_script, command, source="package.json: scripts.test", errors=errors)

    link_script = scripts.get("check-links")
    if not isinstance(link_script, str):
        errors.append("package.json: scripts.check-links must be a string")
    else:
        for command in ("markdown-link-check", "-c .markdown-link-check.json", "src/**/*.md"):
            require_contains(link_script, command, source="package.json: scripts.check-links", errors=errors)

    return errors


def validate_readme() -> list[str]:
    errors: list[str] = []
    readme = Path("README.md").read_text(encoding="utf-8")
    for command in (
        "npm ci",
        "npm test",
        "npm run check:security",
        "npm run check:navigation",
        "npm run check-links",
    ):
        require_contains(readme, command, source="README.md", errors=errors)
    return errors


def validate_workflows() -> list[str]:
    errors: list[str] = []
    expectations = {
        ".github/workflows/book-qa.yml": (
            "npm ci --omit=optional",
            "python3 scripts/check_quality_gates.py",
            "npm run check:security",
        ),
        ".github/workflows/ci.yml": (
            "npm ci",
            "npm run check:quality",
            "npm run check:metadata",
            "npm run check:effort",
            "npm run check:security",
        ),
    }
    for path_str, needles in expectations.items():
        path = Path(path_str)
        text = path.read_text(encoding="utf-8")
        for needle in needles:
            require_contains(text, needle, source=path_str, errors=errors)
    return errors


def main() -> int:
    try:
        package = load_json(Path("package.json"))
    except (CheckError, json.JSONDecodeError) as exc:
        print(exc, file=sys.stderr)
        return 1

    errors: list[str] = []
    errors.extend(validate_package(package))
    errors.extend(validate_readme())
    errors.extend(validate_workflows())

    if errors:
        print("quality gate wiring check failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print("OK: package scripts, README commands, and CI quality-gate wiring match")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
