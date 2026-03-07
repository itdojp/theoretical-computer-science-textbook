import importlib.util
from pathlib import Path


def _load_notation_lint():
    repo_root = Path(__file__).resolve().parents[2]
    script = repo_root / "scripts" / "notation_lint.py"
    spec = importlib.util.spec_from_file_location("notation_lint", script)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_check_file_rejects_full_width_callout_markers(tmp_path, monkeypatch) -> None:
    m = _load_notation_lint()
    path = tmp_path / "sample.md"
    path.write_text("本文\n【チェックリスト】 これは旧式ラベル。\n", encoding="utf-8")
    monkeypatch.setattr(m, "CALLOUT_FREE_PATHS", {path.as_posix()})

    errors = m.check_file(path)

    assert any("Avoid custom full-width callout markers" in err for err in errors)


def test_check_file_rejects_legacy_callout_markers(tmp_path, monkeypatch) -> None:
    m = _load_notation_lint()
    path = tmp_path / "sample.md"
    path.write_text("本文\n〖主張〗 これは旧式ラベル。\n", encoding="utf-8")
    monkeypatch.setattr(m, "CALLOUT_FREE_PATHS", {path.as_posix()})

    errors = m.check_file(path)

    assert any("Avoid custom full-width callout markers" in err for err in errors)


def test_check_file_rejects_mathbb_r_ge_zero_typo(tmp_path, monkeypatch) -> None:
    m = _load_notation_lint()
    path = tmp_path / "sample.md"
    path.write_text("式: \\\\mathbb{R}{\\\\ge 0} \\\\to \\\\mathbb{R}_{\\\\ge 0}\n", encoding="utf-8")
    monkeypatch.setattr(m, "MATHBB_R_GE0_TYPO_PATHS", {path.as_posix()})

    errors = m.check_file(path)

    assert any("Avoid `\\\\mathbb{R}{\\\\ge 0}`" in err for err in errors)
