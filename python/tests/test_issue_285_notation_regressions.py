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


def test_check_file_rejects_ne_l_relation_typo(tmp_path, monkeypatch) -> None:
    m = _load_notation_lint()
    path = tmp_path / "sample.md"
    path.write_text("よって \\\\(x_i \\\\ne_L x_j\\\\) である。\n", encoding="utf-8")
    monkeypatch.setattr(m, "MYHILL_NERODE_NOTATION_PATHS", {path.as_posix()})

    errors = m.check_file(path)

    assert any("Avoid `\\\\ne_L`" in err for err in errors)


def test_check_file_rejects_myhill_nerod_typo(tmp_path, monkeypatch) -> None:
    m = _load_notation_lint()
    path = tmp_path / "sample.md"
    path.write_text("### Myhill-Nerodの定理\n", encoding="utf-8")
    monkeypatch.setattr(m, "MYHILL_NERODE_NOTATION_PATHS", {path.as_posix()})

    errors = m.check_file(path)

    assert any("Avoid `Myhill-Nerod`" in err for err in errors)
