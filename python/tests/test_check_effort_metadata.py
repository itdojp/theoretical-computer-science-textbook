import importlib.util
import json
from pathlib import Path


def _module():
    root = Path(__file__).resolve().parents[2]
    spec = importlib.util.spec_from_file_location("check_effort_metadata", root / "scripts/check_effort_metadata.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _fixture(tmp_path: Path) -> tuple[Path, dict]:
    root = tmp_path
    data = json.loads((Path(__file__).resolve().parents[2] / "docs/_data/chapter_effort.json").read_text())
    (root / "docs/_data").mkdir(parents=True)
    (root / "docs/_layouts").mkdir(parents=True)
    (root / "docs/introduction").mkdir(parents=True)
    (root / "docs/src").mkdir(parents=True)
    (root / "docs/_data/chapter_effort.json").write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    (root / "docs/_layouts/book.html").write_text(
        "{% assign chapter_effort = site.data.chapter_effort.chapters[chapter_key] %}\n"
        "<span>標準学習時間</span>\n"
        "{{ chapter_effort.standard_learning_time | escape }}",
        encoding="utf-8",
    )
    definition_strings = []
    for definition in data["definitions"].values():
        definition_strings += list(definition.values())
    (root / "docs/index.md").write_text("\n".join(definition_strings), encoding="utf-8")
    guide = list(definition_strings)
    guide += [course["display"] for course in data["courses"].values()]
    (root / "docs/introduction/learning-guide.md").write_text("\n".join(guide), encoding="utf-8")
    (root / "docs/book-config.json").write_text("{}", encoding="utf-8")
    return root, data


def test_valid_metadata_passes(tmp_path):
    root, _ = _fixture(tmp_path)
    assert _module().main(["--root", str(root)]) == 0


def test_missing_chapter_fails(tmp_path):
    root, data = _fixture(tmp_path)
    del data["chapters"]["12"]
    (root / "docs/_data/chapter_effort.json").write_text(json.dumps(data), encoding="utf-8")
    assert _module().main(["--root", str(root)]) == 1


def test_changed_chapter_value_makes_total_mismatch_fail(tmp_path):
    root, data = _fixture(tmp_path)
    data["chapters"]["1"]["standard_learning_time"] = "11〜14時間"
    (root / "docs/_data/chapter_effort.json").write_text(json.dumps(data), encoding="utf-8")
    assert _module().main(["--root", str(root)]) == 1


def test_decimal_chapter_sums_are_exact(tmp_path):
    root, data = _fixture(tmp_path)
    data["definitions"]["standard_learning"]["total"] = "0.3〜0.3時間"
    data["courses"]["through"]["display"] = "0.3〜0.3時間（16〜24週、週8時間程度）"
    for number, chapter in data["chapters"].items():
        chapter["standard_learning_time"] = "0〜0時間"
        if number in {"1", "2", "3"}:
            chapter["standard_learning_time"] = "0.1〜0.1時間"
    (root / "docs/_data/chapter_effort.json").write_text(json.dumps(data), encoding="utf-8")
    index = (root / "docs/index.md").read_text(encoding="utf-8")
    index = index.replace("約128〜192時間", "0.3〜0.3時間")
    (root / "docs/index.md").write_text(index, encoding="utf-8")
    guide = (root / "docs/introduction/learning-guide.md").read_text(encoding="utf-8")
    guide = guide.replace("約128〜192時間", "0.3〜0.3時間")
    (root / "docs/introduction/learning-guide.md").write_text(guide, encoding="utf-8")
    assert _module().main(["--root", str(root)]) == 0


def test_legacy_field_fails(tmp_path):
    root, _ = _fixture(tmp_path)
    (root / "docs/chapter-1").mkdir()
    (root / "docs/chapter-1/index.md").write_text("---\nestimated_time: 1時間\n---\n", encoding="utf-8")
    assert _module().main(["--root", str(root)]) == 1


def test_reader_facing_drift_fails(tmp_path):
    root, data = _fixture(tmp_path)
    index = (root / "docs/index.md").read_text(encoding="utf-8")
    index = index.replace(data["definitions"]["standard_learning"]["basis"], "別の前提")
    (root / "docs/index.md").write_text(index, encoding="utf-8")
    assert _module().main(["--root", str(root)]) == 1


def test_commented_layout_contract_fails(tmp_path):
    root, _ = _fixture(tmp_path)
    (root / "docs/_layouts/book.html").write_text(
        "<!-- {% assign chapter_effort = site.data.chapter_effort.chapters[chapter_key] %} "
        "標準学習時間 {{ chapter_effort.standard_learning_time }} -->",
        encoding="utf-8",
    )
    assert _module().main(["--root", str(root)]) == 1
