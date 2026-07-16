import importlib.util
import json
from pathlib import Path


def _module():
    root = Path(__file__).resolve().parents[2]
    script = root / "scripts/check_publication_metadata.py"
    spec = importlib.util.spec_from_file_location("check_publication_metadata", script)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _write(root: Path, relative: str, content: str) -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _fixture(tmp_path: Path) -> Path:
    root = tmp_path
    config = {
        "title": "Test Book",
        "description": "A test book",
        "author": "Test Author",
        "version": "1.2.3",
        "publication": {
            "release_date": "2026-07-16",
            "last_updated": "2026-07-17",
            "release_tag": "v1.2.3",
            "web_is_canonical": True,
            "official_artifacts": ["pdf", "epub"],
        },
        "structure": {"chapters": [{"id": str(number)} for number in range(1, 13)]},
    }
    _write(root, "docs/book-config.json", json.dumps(config))
    _write(
        root,
        "docs/_config.yml",
        '\n'.join(
            (
                'title: "Test Book"',
                'description: "A test book"',
                'author: "Test Author"',
                'version: "1.2.3"',
                'release_date: "2026-07-16"',
                'last_updated: "2026-07-17"',
                'release_tag: "v1.2.3"',
            )
        ),
    )
    _write(
        root,
        "docs/index.md",
        """---
title: "Test Book"
description: "A test book"
author: "Test Author"
version: "1.2.3"
date: "2026-07-16"
last_modified_at: "2026-07-17"
---
Test Book Test Author 1.2.3 2026-07-16 2026-07-17
""",
    )
    introduction = "Test Author 1.2.3 2026-07-16 2026-07-17"
    afterword = "Test Author 1.2.3 2026-07-17"
    for relative in ("docs/introduction/index.md", "src/introduction/index.md"):
        _write(root, relative, introduction)
    for relative in ("docs/afterword/index.md", "src/afterword/index.md"):
        _write(root, relative, afterword)

    package = {"version": "1.2.3", "description": "Test Book", "author": "Test Author"}
    package_lock = {"version": "1.2.3", "packages": {"": {"version": "1.2.3"}}}
    _write(root, "package.json", json.dumps(package))
    _write(root, "package-lock.json", json.dumps(package_lock))
    _write(root, "CLAUDE.md", "Test Book")
    _write(
        root,
        "README.md",
        "Test Book 1.2.3 2026-07-16 v1.2.3 Web版 公式 PDF / EPUB GitHub Releases",
    )

    changelog = "## 1.2.3 — 2026-07-16\nv1.2.3 技術内容の監査と訂正 品質保証"
    downloads = "1.2.3 2026-07-16 v1.2.3 PDF EPUB Web版 GitHub Releases"
    for relative in ("docs/changelog/index.md", "src/changelog/index.md"):
        _write(root, relative, changelog)
    for relative in ("docs/downloads/index.md", "src/downloads/index.md"):
        _write(root, relative, downloads)
    _write(root, "CHANGELOG.md", "docs/changelog/index.md 公開CHANGELOG GitHub Releases")
    _write(
        root,
        ".github/workflows/release-artifacts.yml",
        r'''on:
  push:
    tags:
      - "v*"
jobs:
  build:
    steps:
      - name: Setup Python
        uses: actions/setup-python@v6
        with:
          python-version: "3.12"
      - name: Verify canonical publication metadata and release tag
        run: |
          python3 scripts/check_publication_metadata.py --release-tag "${GITHUB_REF_NAME}"
      - name: Resolve filesystem-safe artifact label
        id: artifact_label
        run: |
          artifact_label="${GITHUB_REF_NAME//\//-}"
          echo "value=${artifact_label}" >> "${GITHUB_OUTPUT}"
      - name: Build EPUB
        run: |
          artifact_label="${{ steps.artifact_label.outputs.value }}"
          pandoc input -o "dist/theoretical-computer-science-textbook-${artifact_label}.epub"
      - name: Build PDF
        run: |
          artifact_label="${{ steps.artifact_label.outputs.value }}"
          pandoc input -o "dist/theoretical-computer-science-textbook-${artifact_label}.pdf"
      - name: Upload workflow artifacts
        uses: actions/upload-artifact@v7
        with:
          path: |
            dist/theoretical-computer-science-textbook-*.pdf
            dist/theoretical-computer-science-textbook-*.epub
      - name: Create GitHub Release and upload assets
        if: startsWith(github.ref, 'refs/tags/')
        uses: softprops/action-gh-release@v3
        with:
          files: |
            dist/theoretical-computer-science-textbook-${{ steps.artifact_label.outputs.value }}.pdf
            dist/theoretical-computer-science-textbook-${{ steps.artifact_label.outputs.value }}.epub
''',
    )
    _write(
        root,
        "scripts/build_offline_book.py",
        r'''DEFAULT = "docs/book-config.json"


def build_publication_front_matter(cfg):
    release_date = ""
    last_updated = ""
    return f"date: {release_date}\nlast_updated: {last_updated}"


def main():
    cfg = load_book_config(Path(args.config))
    out_path.write_text(build_publication_front_matter(cfg) + combined_text)
''',
    )
    return root


def test_happy_path_and_release_tag(tmp_path):
    root = _fixture(tmp_path)
    assert _module().main(["--root", str(root), "--release-tag", "v1.2.3"]) == 0


def test_consumer_front_matter_drift_fails(tmp_path):
    root = _fixture(tmp_path)
    index = root / "docs/index.md"
    index.write_text(index.read_text(encoding="utf-8").replace('version: "1.2.3"', 'version: "9.9.9"'), encoding="utf-8")
    assert _module().main(["--root", str(root)]) == 1


def test_legacy_root_config_fails(tmp_path):
    root = _fixture(tmp_path)
    _write(root, "book-config.json", "{}")
    assert _module().main(["--root", str(root)]) == 1


def test_release_tag_argument_mismatch_fails(tmp_path):
    root = _fixture(tmp_path)
    assert _module().main(["--root", str(root), "--release-tag", "v9.9.9"]) == 1


def test_missing_artifact_and_workflow_contracts_fail(tmp_path):
    root = _fixture(tmp_path)
    config_path = root / "docs/book-config.json"
    config = json.loads(config_path.read_text(encoding="utf-8"))
    config["publication"]["official_artifacts"] = ["pdf"]
    config_path.write_text(json.dumps(config), encoding="utf-8")
    _write(root, ".github/workflows/release-artifacts.yml", "")
    assert _module().main(["--root", str(root)]) == 1


def test_src_mirror_drift_fails(tmp_path):
    root = _fixture(tmp_path)
    _write(root, "src/changelog/index.md", "stale mirror")
    assert _module().main(["--root", str(root)]) == 1


def test_package_lock_version_drift_fails(tmp_path):
    root = _fixture(tmp_path)
    package_lock_path = root / "package-lock.json"
    package_lock = json.loads(package_lock_path.read_text(encoding="utf-8"))
    package_lock["packages"][""]["version"] = "1.2.2"
    package_lock_path.write_text(json.dumps(package_lock), encoding="utf-8")
    assert _module().main(["--root", str(root)]) == 1


def test_malformed_package_lock_fails_without_crashing(tmp_path):
    root = _fixture(tmp_path)
    _write(root, "package-lock.json", '{"version":"1.2.3","packages":[]}')
    assert _module().main(["--root", str(root)]) == 1


def test_malformed_publication_fails_without_crashing(tmp_path):
    root = _fixture(tmp_path)
    config_path = root / "docs/book-config.json"
    config = json.loads(config_path.read_text(encoding="utf-8"))
    config["publication"] = {"release_date": "2026-02-30"}
    config_path.write_text(json.dumps(config), encoding="utf-8")
    assert _module().main(["--root", str(root)]) == 1


def test_workflow_contracts_in_comments_do_not_pass(tmp_path):
    root = _fixture(tmp_path)
    _write(
        root,
        ".github/workflows/release-artifacts.yml",
        """# tags:
#       - \"v*\"
# check_publication_metadata.py --release-tag \"${GITHUB_REF_NAME}\"
# GITHUB_REF_NAME//\\//-
# pandoc -o fake.pdf
# pandoc -o fake.epub
# uses: actions/upload-artifact@v7
# uses: softprops/action-gh-release@v3
jobs: {}
""",
    )
    assert _module().main(["--root", str(root)]) == 1


def test_workflow_requires_slash_safe_artifact_label(tmp_path):
    root = _fixture(tmp_path)
    workflow = root / ".github/workflows/release-artifacts.yml"
    text = workflow.read_text(encoding="utf-8").replace(
        "GITHUB_REF_NAME//\\//-", "GITHUB_REF_NAME"
    )
    workflow.write_text(text, encoding="utf-8")
    assert _module().main(["--root", str(root)]) == 1


def test_builder_contracts_in_comments_do_not_pass(tmp_path):
    root = _fixture(tmp_path)
    _write(
        root,
        "scripts/build_offline_book.py",
        """# docs/book-config.json
# build_publication_front_matter(cfg)
# date: {release_date}
# last_updated: {last_updated}
value = 1
""",
    )
    assert _module().main(["--root", str(root)]) == 1
