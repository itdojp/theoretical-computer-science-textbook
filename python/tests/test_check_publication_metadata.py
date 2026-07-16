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
            "release_status": "published",
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
                'release_status: "published"',
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
    release_url = (
        "https://github.com/itdojp/theoretical-computer-science-textbook/"
        "releases/tag/v1.2.3"
    )
    _write(
        root,
        "README.md",
        "Test Book 1.2.3 2026-07-16 v1.2.3 Web版 公式 PDF / EPUB "
        f"GitHub Releases {release_url}",
    )

    changelog = (
        "## 1.2.3 — 2026-07-16\n"
        f"v1.2.3 技術内容の監査と訂正 品質保証 {release_url}"
    )
    asset_base = (
        "https://github.com/itdojp/theoretical-computer-science-textbook/"
        "releases/download/v1.2.3/theoretical-computer-science-textbook-v1.2.3"
    )
    downloads = (
        "1.2.3 2026-07-16 v1.2.3 PDF EPUB Web版 GitHub Releases "
        f"{release_url} {asset_base}.pdf {asset_base}.epub"
    )
    for relative in ("docs/changelog/index.md", "src/changelog/index.md"):
        _write(root, relative, changelog)
    for relative in ("docs/downloads/index.md", "src/downloads/index.md"):
        _write(root, relative, downloads)
    _write(root, "CHANGELOG.md", "docs/changelog/index.md 公開CHANGELOG GitHub Releases")
    _write(
        root,
        ".github/workflows/release-artifacts.yml",
        r'''on:
  workflow_dispatch:
    inputs:
      release_tag:
        required: false
        type: string
  push:
    tags:
      - "v*"
permissions:
  contents: read
jobs:
  build:
    outputs:
      release_tag: ${{ steps.release_target.outputs.release_tag }}
      artifact_label: ${{ steps.artifact_label.outputs.value }}
    steps:
      - name: Checkout release tooling
        uses: actions/checkout@v6
        with:
          ref: main
          path: release-tooling
          persist-credentials: false
      - name: Resolve release target
        id: release_target
        env:
          REQUESTED_RELEASE_TAG: ${{ inputs.release_tag || '' }}
        run: |
          if [[ "${GITHUB_EVENT_NAME}" == "workflow_dispatch" ]] && [[ "${GITHUB_REF}" != "refs/heads/main" ]]; then exit 1; fi
          if [[ -n "${release_tag}" ]] && [[ "${release_tag}" =~ ^v[0-9]+\.[0-9]+\.[0-9]+$ ]]; then true; fi
          echo "target_ref=${target_ref}" >> "${GITHUB_OUTPUT}"
          echo "release_tag=${release_tag}" >> "${GITHUB_OUTPUT}"
          echo "artifact_source=${artifact_source}" >> "${GITHUB_OUTPUT}"
      - name: Checkout release source
        uses: actions/checkout@v6
        with:
          ref: ${{ steps.release_target.outputs.target_ref }}
          path: release-source
          fetch-depth: 0
          persist-credentials: false
      - name: Setup Python
        uses: actions/setup-python@v6
        with:
          python-version: "3.12"
      - name: Verify canonical publication metadata and release tag
        run: |
          if [[ -n "${RELEASE_TAG}" ]]; then
            source_head="$(git -C release-source rev-parse HEAD)"
            tag_head="$(git -C release-source rev-list -n 1 "${RELEASE_TAG}")"
            test "${source_head}" = "${tag_head}"
            python3 release-tooling/scripts/check_publication_metadata.py \
              --root release-source --contract-root release-tooling \
              --release-tag "${RELEASE_TAG}"
          else
            python3 release-tooling/scripts/check_publication_metadata.py \
              --root release-source --contract-root release-tooling
          fi
      - name: Resolve filesystem-safe artifact label
        id: artifact_label
        env:
          ARTIFACT_SOURCE: ${{ steps.release_target.outputs.artifact_source }}
        run: |
          artifact_label="${ARTIFACT_SOURCE//\//-}"
          echo "value=${artifact_label}" >> "${GITHUB_OUTPUT}"
      - name: Build offline sources (Markdown)
        run: |
          python3 release-tooling/scripts/build_offline_book.py \
            --docs-root release-source/docs \
            --config release-source/docs/book-config.json \
            --target epub --out dist/book.epub.md
          python3 release-tooling/scripts/build_offline_book.py \
            --docs-root release-source/docs \
            --config release-source/docs/book-config.json \
            --target pdf --out dist/book.pdf.md --asset-out dist
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
          name: offline-artifacts
          path: |
            dist/theoretical-computer-science-textbook-*.pdf
            dist/theoretical-computer-science-textbook-*.epub
  publish:
    needs: build
    if: needs.build.outputs.release_tag != ''
    permissions:
      actions: read
      contents: write
    steps:
      - name: Download verified workflow artifacts
        uses: actions/download-artifact@v8
        with:
          name: offline-artifacts
          path: dist
      - name: Create GitHub Release and upload assets
        uses: softprops/action-gh-release@v3
        with:
          tag_name: ${{ needs.build.outputs.release_tag }}
          files: |
            dist/theoretical-computer-science-textbook-${{ needs.build.outputs.artifact_label }}.pdf
            dist/theoretical-computer-science-textbook-${{ needs.build.outputs.artifact_label }}.epub
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


def normalize_math_delimiters_for_pandoc(text):
    return text


def preprocess_markdown(text):
    return normalize_math_delimiters_for_pandoc(text)


def main():
    cfg = load_book_config(Path(args.config))
    out_path.write_text(build_publication_front_matter(cfg) + combined_text)
''',
    )
    return root


def _set_release_status(root: Path, status: str) -> None:
    config_path = root / "docs/book-config.json"
    config = json.loads(config_path.read_text(encoding="utf-8"))
    config["publication"]["release_status"] = status
    config_path.write_text(json.dumps(config), encoding="utf-8")
    config_yml = root / "docs/_config.yml"
    config_yml.write_text(
        config_yml.read_text(encoding="utf-8").replace(
            'release_status: "published"', f'release_status: "{status}"'
        ),
        encoding="utf-8",
    )


def _remove_release_status(root: Path) -> None:
    config_path = root / "docs/book-config.json"
    config = json.loads(config_path.read_text(encoding="utf-8"))
    del config["publication"]["release_status"]
    config_path.write_text(json.dumps(config), encoding="utf-8")
    config_yml = root / "docs/_config.yml"
    config_yml.write_text(
        config_yml.read_text(encoding="utf-8").replace(
            'release_status: "published"\n', ""
        ),
        encoding="utf-8",
    )


def _replace_fixture_version(root: Path, old: str, new: str) -> None:
    for path in root.rglob("*"):
        if path.is_file():
            path.write_text(
                path.read_text(encoding="utf-8").replace(old, new),
                encoding="utf-8",
            )


def _write_preparing_reader_copy(root: Path) -> None:
    _write(
        root,
        "README.md",
        "Test Book 1.2.3 2026-07-16 v1.2.3 Web版 公式 PDF / EPUB "
        "GitHub Releases Release準備中",
    )
    changelog = (
        "## 1.2.3 — 2026-07-16\n"
        "v1.2.3 技術内容の監査と訂正 品質保証 Release完了後"
    )
    downloads = (
        "1.2.3 2026-07-16 v1.2.3 PDF EPUB Web版 GitHub Releases 配布予定tag"
    )
    for relative in ("docs/changelog/index.md", "src/changelog/index.md"):
        _write(root, relative, changelog)
    for relative in ("docs/downloads/index.md", "src/downloads/index.md"):
        _write(root, relative, downloads)


def test_happy_path_and_release_tag(tmp_path):
    root = _fixture(tmp_path)
    assert _module().main(["--root", str(root), "--release-tag", "v1.2.3"]) == 0


def test_happy_path_without_release_tag(tmp_path):
    root = _fixture(tmp_path)
    assert _module().main(["--root", str(root)]) == 0


def test_current_publication_requires_release_status(tmp_path):
    root = _fixture(tmp_path)
    _remove_release_status(root)

    assert _module().main(["--root", str(root)]) == 1


def test_immutable_legacy_release_source_without_status_remains_retryable(tmp_path):
    root = _fixture(tmp_path)
    _replace_fixture_version(root, "1.2.3", "1.2.0")
    _remove_release_status(root)

    assert _module().main(
        ["--root", str(root), "--release-tag", "v1.2.0"]
    ) == 0


def test_nonlegacy_release_source_without_status_fails(tmp_path):
    root = _fixture(tmp_path)
    _remove_release_status(root)

    assert _module().main(
        ["--root", str(root), "--release-tag", "v1.2.3"]
    ) == 1


def test_published_status_rejects_stale_reader_copy(tmp_path):
    root = _fixture(tmp_path)
    readme = root / "README.md"
    readme.write_text(
        readme.read_text(encoding="utf-8") + " Release準備中",
        encoding="utf-8",
    )

    assert _module().main(["--root", str(root)]) == 1


def test_preparing_status_requires_preparation_copy_and_rejects_current_release_links(
    tmp_path,
):
    root = _fixture(tmp_path)
    _set_release_status(root, "preparing")

    assert _module().main(["--root", str(root)]) == 1


def test_preparing_status_with_synchronized_reader_copy_passes(tmp_path):
    root = _fixture(tmp_path)
    _set_release_status(root, "preparing")
    _write_preparing_reader_copy(root)

    assert _module().main(["--root", str(root)]) == 0


def test_preparing_status_rejects_asset_links_outside_downloads(tmp_path):
    root = _fixture(tmp_path)
    _set_release_status(root, "preparing")
    _write_preparing_reader_copy(root)
    asset_base = (
        "https://github.com/itdojp/theoretical-computer-science-textbook/"
        "releases/download/v1.2.3/theoretical-computer-science-textbook-v1.2.3"
    )
    readme = root / "README.md"
    readme.write_text(
        readme.read_text(encoding="utf-8") + f" {asset_base}.pdf",
        encoding="utf-8",
    )
    changelog = root / "docs/changelog/index.md"
    changed = changelog.read_text(encoding="utf-8") + f" {asset_base}.epub"
    changelog.write_text(changed, encoding="utf-8")
    _write(root, "src/changelog/index.md", changed)

    assert _module().main(["--root", str(root)]) == 1


def test_unknown_release_status_fails(tmp_path):
    root = _fixture(tmp_path)
    config_path = root / "docs/book-config.json"
    config = json.loads(config_path.read_text(encoding="utf-8"))
    config["publication"]["release_status"] = "available"
    config_path.write_text(json.dumps(config), encoding="utf-8")

    assert _module().main(["--root", str(root)]) == 1


def test_trusted_contract_root_does_not_execute_release_source_code(tmp_path):
    source = _fixture(tmp_path / "source")
    tooling = _fixture(tmp_path / "tooling")
    _write(source, "scripts/check_publication_metadata.py", "raise RuntimeError('untrusted')")

    assert (
        _module().main(
            [
                "--root",
                str(source),
                "--contract-root",
                str(tooling),
                "--release-tag",
                "v1.2.3",
            ]
        )
        == 0
    )


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
        "ARTIFACT_SOURCE//\\//-", "ARTIFACT_SOURCE"
    )
    workflow.write_text(text, encoding="utf-8")
    assert _module().main(["--root", str(root)]) == 1


def test_workflow_rejects_duplicate_step_name_shadowing(tmp_path):
    root = _fixture(tmp_path)
    workflow = root / ".github/workflows/release-artifacts.yml"
    text = workflow.read_text(encoding="utf-8")
    duplicate = "      - name: Resolve filesystem-safe artifact label\n        run: true\n"
    workflow.write_text(text.replace("    steps:\n", f"    steps:\n{duplicate}", 1), encoding="utf-8")

    assert _module().main(["--root", str(root)]) == 1


def test_workflow_requires_manual_release_input_and_dual_checkout(tmp_path):
    root = _fixture(tmp_path)
    workflow = root / ".github/workflows/release-artifacts.yml"
    text = workflow.read_text(encoding="utf-8")
    text = text.replace("      release_tag:\n", "      retry_tag:\n")
    text = text.replace(
        "ref: ${{ steps.release_target.outputs.target_ref }}",
        "ref: main",
    )
    workflow.write_text(text, encoding="utf-8")

    assert _module().main(["--root", str(root)]) == 1


def test_workflow_requires_trusted_tooling_and_source_tag_equality(tmp_path):
    root = _fixture(tmp_path)
    workflow = root / ".github/workflows/release-artifacts.yml"
    text = workflow.read_text(encoding="utf-8")
    text = text.replace("          ref: main\n", "")
    text = text.replace(
        '          test "${source_head}" = "${tag_head}"\n',
        "          true\n",
    )
    workflow.write_text(text, encoding="utf-8")

    assert _module().main(["--root", str(root)]) == 1


def test_workflow_requires_artifact_only_source_validation(tmp_path):
    root = _fixture(tmp_path)
    workflow = root / ".github/workflows/release-artifacts.yml"
    text = workflow.read_text(encoding="utf-8")
    artifact_only = (
        "          else\n"
        "            python3 release-tooling/scripts/check_publication_metadata.py \\\n"
        "              --root release-source --contract-root release-tooling\n"
    )
    workflow.write_text(text.replace(artifact_only, ""), encoding="utf-8")

    assert _module().main(["--root", str(root)]) == 1


def test_workflow_rejects_release_source_code_execution(tmp_path):
    root = _fixture(tmp_path)
    workflow = root / ".github/workflows/release-artifacts.yml"
    text = workflow.read_text(encoding="utf-8").replace(
        "python3 release-tooling/scripts/check_publication_metadata.py",
        "python3 release-source/scripts/check_publication_metadata.py",
    )
    workflow.write_text(text, encoding="utf-8")

    assert _module().main(["--root", str(root)]) == 1


def test_workflow_requires_read_build_and_isolated_write_publish(tmp_path):
    root = _fixture(tmp_path)
    workflow = root / ".github/workflows/release-artifacts.yml"
    text = workflow.read_text(encoding="utf-8")
    text = text.replace("permissions:\n  contents: read", "permissions:\n  contents: write", 1)
    text = text.replace("      contents: write", "      contents: read")
    workflow.write_text(text, encoding="utf-8")

    assert _module().main(["--root", str(root)]) == 1


def test_workflow_requires_validated_release_gate_and_tag_name(tmp_path):
    root = _fixture(tmp_path)
    workflow = root / ".github/workflows/release-artifacts.yml"
    text = workflow.read_text(encoding="utf-8")
    text = text.replace(
        "if: needs.build.outputs.release_tag != ''",
        "if: github.event_name == 'workflow_dispatch'",
    )
    text = text.replace(
        "tag_name: ${{ needs.build.outputs.release_tag }}",
        "tag_name: v9.9.9",
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


def test_builder_math_normalizer_must_be_on_preprocess_path(tmp_path):
    root = _fixture(tmp_path)
    builder = root / "scripts/build_offline_book.py"
    text = builder.read_text(encoding="utf-8").replace(
        "return normalize_math_delimiters_for_pandoc(text)",
        "return text",
    )
    builder.write_text(text, encoding="utf-8")

    assert _module().main(["--root", str(root)]) == 1
