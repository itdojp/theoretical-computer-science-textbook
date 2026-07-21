from __future__ import annotations

import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from check_theorem_contracts import (  # noqa: E402
    BYZANTINE_ALTERNATIVES,
    BYZANTINE_FORBIDDEN_PATTERNS,
    BYZANTINE_PRIMARY_SOURCE,
    BYZANTINE_REQUIREMENTS,
    check_repository,
    validate_byzantine_theorem,
)


def _production_chapter() -> str:
    return (ROOT / "src" / "chapter-12" / "index.md").read_text(encoding="utf-8")


def test_production_byzantine_theorem_satisfies_contract() -> None:
    text = _production_chapter()

    assert validate_byzantine_theorem(text, source="chapter-12") == []


@pytest.mark.parametrize(
    ("requirement", "snippet"),
    [
        (requirement, snippet)
        for requirement, snippets in BYZANTINE_REQUIREMENTS.items()
        for snippet in snippets
    ],
)
def test_contract_rejects_each_missing_byzantine_obligation(
    requirement: str, snippet: str
) -> None:
    text = _production_chapter()
    assert snippet in text

    errors = validate_byzantine_theorem(text.replace(snippet, ""), source="chapter-12")

    assert any(f"requirement {requirement!r}" in error for error in errors)


def test_contract_rejects_missing_primary_source() -> None:
    text = _production_chapter()

    errors = validate_byzantine_theorem(
        text.replace(BYZANTINE_PRIMARY_SOURCE, ""), source="chapter-12"
    )

    assert any("must cite primary source" in error for error in errors)


@pytest.mark.parametrize(
    ("requirement", "alternatives"), BYZANTINE_ALTERNATIVES.items()
)
def test_contract_accepts_supported_wording_alternative(
    requirement: str, alternatives: tuple[str, ...]
) -> None:
    text = _production_chapter()
    primary, alternative = alternatives
    assert primary in text

    errors = validate_byzantine_theorem(
        text.replace(primary, alternative), source="chapter-12"
    )

    assert not any(f"alternative requirement {requirement!r}" in error for error in errors)


@pytest.mark.parametrize(
    ("requirement", "alternatives"), BYZANTINE_ALTERNATIVES.items()
)
def test_contract_rejects_missing_wording_alternative(
    requirement: str, alternatives: tuple[str, ...]
) -> None:
    text = _production_chapter()
    for alternative in alternatives:
        text = text.replace(alternative, "")

    errors = validate_byzantine_theorem(text, source="chapter-12")

    assert any(f"alternative requirement {requirement!r}" in error for error in errors)


@pytest.mark.parametrize(
    ("description", "contradiction"),
    [
        ("n=3f described as possible", r"\\(n=3f\\) でも合意可能である。"),
        ("OM(f) described as unnecessary", "OM(f) は不要である。"),
        (
            "oral-message threshold applied to signed model",
            "signed messages model にも n > 3f を適用する。",
        ),
    ],
)
def test_contract_rejects_explicit_contradictions(
    description: str, contradiction: str
) -> None:
    text = _production_chapter().replace(
        "#### FLP 不可能性定理", f"{contradiction}\n\n#### FLP 不可能性定理"
    )

    errors = validate_byzantine_theorem(text, source="chapter-12")

    assert any(description in error for error in errors)


def test_contract_allows_n_3f_plus_one_possible_wording() -> None:
    text = _production_chapter().replace(
        "#### FLP 不可能性定理",
        r"\\(n=3f+1\\) でも合意可能である。" + "\n\n#### FLP 不可能性定理",
    )

    errors = validate_byzantine_theorem(text, source="chapter-12")

    assert not any("n=3f described as possible" in error for error in errors)


def test_contract_rejects_misordered_proof_blocks() -> None:
    text = _production_chapter()
    sufficiency_start = text.index("**十分性（")
    necessity_start = text.index("**必要性（")
    boundary_start = text.index("**境界**", necessity_start)
    flp_start = text.index("#### FLP 不可能性定理", boundary_start)
    sufficiency = text[sufficiency_start:necessity_start]
    necessity = text[necessity_start:boundary_start]
    reordered = text[:sufficiency_start] + necessity + sufficiency + text[boundary_start:flp_start] + text[flp_start:]

    errors = validate_byzantine_theorem(reordered, source="chapter-12")

    assert any("must be ordered" in error for error in errors)


@pytest.mark.parametrize("block_start", ["**十分性（", "**必要性（", "**境界**"])
def test_contract_rejects_missing_proof_block(block_start: str) -> None:
    text = _production_chapter().replace(block_start, "**削除済み（", 1)

    errors = validate_byzantine_theorem(text, source="chapter-12")

    assert any("must contain exactly one" in error for error in errors)


def test_repository_contract_rejects_src_docs_drift(tmp_path: Path) -> None:
    src = tmp_path / "src.md"
    docs = tmp_path / "docs.md"
    text = _production_chapter()
    src.write_text(text, encoding="utf-8")
    docs.write_text(text + "\n", encoding="utf-8")

    errors = check_repository(src, docs)

    assert f"{src} and {docs} differ" in errors


def test_contract_rejects_missing_section_boundary() -> None:
    text = _production_chapter().replace("#### FLP 不可能性定理", "")

    errors = validate_byzantine_theorem(text, source="chapter-12")

    assert any("must contain exactly one" in error for error in errors)
