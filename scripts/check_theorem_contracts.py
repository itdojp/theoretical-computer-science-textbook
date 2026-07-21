#!/usr/bin/env python3
"""Guard theorem statements whose assumptions and proof directions must stay aligned."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


BYZANTINE_START = "#### Byzantine 将軍問題"
BYZANTINE_END = "#### FLP 不可能性定理"
BYZANTINE_PRIMARY_SOURCE = "https://lamport.azurewebsites.net/pubs/byz.pdf"
BYZANTINE_SUFFICIENCY_START = "**十分性（"
BYZANTINE_NECESSITY_START = "**必要性（"
BYZANTINE_BOUNDARY_START = "**境界**"

BYZANTINE_REQUIREMENTS: dict[str, tuple[str, ...]] = {
    "agreement contract": (
        "commander",
        "lieutenant",
        "**IC1**",
        "**IC2**",
    ),
    "oral-messages model": (
        "**モデル（oral messages）**",
        "完全結合",
        r"\\(n\\ge 3\\)",
        r"最大 \\(f\\)",
        "偽造不能な署名は使わない",
    ),
    "oral-messages assumptions": (
        "**A1（配送）**",
        "**A2（送信者識別）**",
        "**A3（欠落検出）**",
        "timeout",
        "メッセージ生成・配送時間には既知の上界",
        "時計のずれにも既知の上界",
    ),
    "necessary-and-sufficient theorem": (
        "{: #thm-12-3 }",
        "必要十分条件",
        r"\\(n > 3f\\)",
    ),
    "OM(f) sufficiency": (
        r"\\(OM(0)\\)",
        r"\\(OM(m)\\)",
        r"\\(OM(m-1)\\)",
        r"\\(OM(f)\\)",
        "帰納法",
        "原論文はラウンド数ではなく",
        r"メッセージ経路長が最大 \\(f+1\\)",
        r"\\(f+1\\) ラウンド",
    ),
    "n <= 3f necessity": (
        "3群",
        "3プロセス・1故障",
        "局所的に識別できない",
    ),
    "boundary cases": (
        r"\\(n=3f\\)",
        r"\\(n=3f+1\\)",
        r"\\(OM(1)\\)",
        "2ラウンド",
        "2プロセス指令問題は IC1 が自明",
        "written messages model は A4",
        r"\\(SM(m)\\)",
        r"\\(n>3f\\) の閾値は適用しない",
    ),
}

BYZANTINE_REQUIREMENT_SCOPES = {
    "agreement contract": "preamble",
    "oral-messages model": "preamble",
    "oral-messages assumptions": "preamble",
    "necessary-and-sufficient theorem": "preamble",
    "OM(f) sufficiency": "sufficiency",
    "n <= 3f necessity": "necessity",
    "boundary cases": "boundary",
}

BYZANTINE_ALTERNATIVES: dict[str, tuple[str, ...]] = {
    "point-to-point transport": ("point-to-point", "点対点"),
    "deterministic aggregation": ("majority", "多数決"),
}

BYZANTINE_FORBIDDEN_PATTERNS: dict[str, str] = {
    "n=3f described as possible": r"n\s*=\s*3f.{0,20}(?:でも|で).{0,20}(?<!不)可能",
    "OM(f) described as unnecessary": r"OM\(f\).{0,30}不要",
    "oral-message threshold applied to signed model": (
        r"(?:signed|written) messages model.{0,80}n\s*>\s*3f"
        r".{0,40}(?:適用する|必要である)"
    ),
}


def extract_unique_section(text: str, *, source: str) -> tuple[str, list[str]]:
    """Return the unique Byzantine section and structural errors."""
    errors: list[str] = []
    if text.count(BYZANTINE_START) != 1:
        errors.append(f"{source}: must contain exactly one {BYZANTINE_START!r} heading")
        return "", errors
    if text.count(BYZANTINE_END) != 1:
        errors.append(f"{source}: must contain exactly one {BYZANTINE_END!r} heading")
        return "", errors

    start = text.index(BYZANTINE_START)
    end = text.index(BYZANTINE_END)
    if end <= start:
        errors.append(f"{source}: Byzantine section must precede the FLP section")
        return "", errors
    return text[start:end], errors


def validate_byzantine_theorem(text: str, *, source: str) -> list[str]:
    """Check explicit obligations; mathematical review remains human-owned."""
    section, errors = extract_unique_section(text, source=source)
    if not section:
        return errors

    starts = {
        "sufficiency": section.count(BYZANTINE_SUFFICIENCY_START),
        "necessity": section.count(BYZANTINE_NECESSITY_START),
        "boundary": section.count(BYZANTINE_BOUNDARY_START),
    }
    for name, count in starts.items():
        if count != 1:
            errors.append(f"{source}: Byzantine section must contain exactly one {name} block")
    if errors:
        return errors

    sufficiency_start = section.index(BYZANTINE_SUFFICIENCY_START)
    necessity_start = section.index(BYZANTINE_NECESSITY_START)
    boundary_start = section.index(BYZANTINE_BOUNDARY_START)
    if not sufficiency_start < necessity_start < boundary_start:
        errors.append(
            f"{source}: Byzantine proof blocks must be ordered sufficiency, necessity, boundary"
        )
        return errors

    scoped_text = {
        "preamble": section[:sufficiency_start],
        "sufficiency": section[sufficiency_start:necessity_start],
        "necessity": section[necessity_start:boundary_start],
        "boundary": section[boundary_start:],
    }
    for requirement, snippets in BYZANTINE_REQUIREMENTS.items():
        scope = BYZANTINE_REQUIREMENT_SCOPES[requirement]
        missing = [snippet for snippet in snippets if snippet not in scoped_text[scope]]
        if missing:
            errors.append(
                f"{source}: Byzantine theorem requirement {requirement!r} "
                f"is missing {missing}"
            )

    for requirement, alternatives in BYZANTINE_ALTERNATIVES.items():
        if not any(alternative in section for alternative in alternatives):
            errors.append(
                f"{source}: Byzantine theorem alternative requirement {requirement!r} "
                f"needs one of {list(alternatives)}"
            )

    for description, pattern in BYZANTINE_FORBIDDEN_PATTERNS.items():
        if re.search(pattern, section, flags=re.DOTALL):
            errors.append(
                f"{source}: Byzantine theorem contains forbidden contradiction: {description}"
            )

    if BYZANTINE_PRIMARY_SOURCE not in text:
        errors.append(
            f"{source}: Byzantine theorem must cite primary source "
            f"{BYZANTINE_PRIMARY_SOURCE}"
        )
    return errors


def check_repository(src_path: Path, docs_path: Path) -> list[str]:
    errors: list[str] = []
    src = src_path.read_text(encoding="utf-8")
    docs = docs_path.read_text(encoding="utf-8")
    if src != docs:
        errors.append(f"{src_path} and {docs_path} differ")
    errors.extend(validate_byzantine_theorem(src, source=str(src_path)))
    errors.extend(validate_byzantine_theorem(docs, source=str(docs_path)))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--src", default="src/chapter-12/index.md")
    parser.add_argument("--docs", default="docs/chapter-12/index.md")
    args = parser.parse_args()

    errors = check_repository(Path(args.src), Path(args.docs))
    if errors:
        print("theorem contract check failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("ok: Byzantine theorem model, necessity, sufficiency, boundary, and source")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
