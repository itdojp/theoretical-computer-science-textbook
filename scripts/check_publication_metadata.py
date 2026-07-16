#!/usr/bin/env python3
"""Validate canonical publication metadata and release contracts."""

from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from datetime import date
from pathlib import Path
from typing import Any

SEMVER_RE = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
CHAPTER_IDS = {str(number) for number in range(1, 13)}
LEGACY_TITLE = "理論計算機科学教本 - コンピュータサイエンス基礎理論"
RELEASE_BASE_URL = (
    "https://github.com/itdojp/theoretical-computer-science-textbook/releases"
)
RELEASE_STATUSES = {"preparing", "published"}
STALE_PUBLISHED_COPY = ("Release準備中", "Release完了後", "配布予定tag")


def _read(path: Path, errors: list[str]) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        errors.append(f"{path}: cannot read file: {exc}")
        return ""


def _load_json(path: Path, errors: list[str]) -> Any:
    text = _read(path, errors)
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        errors.append(f"{path}: invalid JSON: {exc}")
        return None


def _required_string(value: Any, name: str, errors: list[str]) -> str | None:
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{name}: required non-empty string")
        return None
    return value


def _parse_date(value: str | None, name: str, errors: list[str]) -> date | None:
    if value is None:
        return None
    if not DATE_RE.fullmatch(value):
        errors.append(f"{name}: must be ISO date YYYY-MM-DD")
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        errors.append(f"{name}: invalid calendar date")
        return None


def validate_config(root: Path, errors: list[str]) -> dict[str, Any] | None:
    path = root / "docs/book-config.json"
    cfg = _load_json(path, errors)
    if not isinstance(cfg, dict):
        errors.append(f"{path}: top-level value must be an object")
        return None

    values = {
        key: _required_string(cfg.get(key), key, errors)
        for key in ("title", "description", "author", "version")
    }
    version = values["version"]
    if version is not None and not SEMVER_RE.fullmatch(version):
        errors.append("version: must be a semantic version X.Y.Z")

    publication = cfg.get("publication")
    if not isinstance(publication, dict):
        errors.append("publication: required object")
        publication = {}
    release_date = _required_string(
        publication.get("release_date"), "publication.release_date", errors
    )
    last_updated = _required_string(
        publication.get("last_updated"), "publication.last_updated", errors
    )
    release_tag = _required_string(
        publication.get("release_tag"), "publication.release_tag", errors
    )
    release_status_value = publication.get("release_status")
    release_status = (
        None
        if release_status_value is None
        else _required_string(
            release_status_value, "publication.release_status", errors
        )
    )
    if release_status is not None and release_status not in RELEASE_STATUSES:
        errors.append(
            "publication.release_status: must be one of "
            f"{sorted(RELEASE_STATUSES)!r}"
        )
    parsed_release = _parse_date(release_date, "publication.release_date", errors)
    parsed_updated = _parse_date(last_updated, "publication.last_updated", errors)
    if parsed_release is not None and parsed_updated is not None and parsed_updated < parsed_release:
        errors.append("publication.last_updated: must be on or after release_date")
    if version is not None and release_tag is not None and release_tag != f"v{version}":
        errors.append("publication.release_tag: must equal v{version}")
    if publication.get("web_is_canonical") is not True:
        errors.append("publication.web_is_canonical: must be true")
    if publication.get("official_artifacts") != ["pdf", "epub"]:
        errors.append("publication.official_artifacts: must be exactly ['pdf', 'epub']")

    structure = cfg.get("structure")
    chapters = structure.get("chapters") if isinstance(structure, dict) else None
    chapter_ids = (
        [str(chapter.get("id")) for chapter in chapters]
        if isinstance(chapters, list) and all(isinstance(chapter, dict) for chapter in chapters)
        else []
    )
    if len(chapter_ids) != 12 or set(chapter_ids) != CHAPTER_IDS:
        errors.append("structure.chapters: must contain exactly chapters 1 through 12")

    legacy_config = root / "book-config.json"
    if legacy_config.exists():
        errors.append(f"{legacy_config}: legacy root config must be absent")
    return cfg


def _yaml_value(text: str, key: str) -> str | None:
    match = re.search(rf"(?m)^{re.escape(key)}:\s*(.*?)\s*$", text)
    if match is None:
        return None
    return match.group(1).strip().strip('"').strip("'")


def _front_matter(text: str) -> str:
    match = re.match(r"\A---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    return match.group(1) if match else ""


def _check_yaml_values(
    path: Path, text: str, expected: dict[str, str], errors: list[str]
) -> None:
    for key, value in expected.items():
        actual = _yaml_value(text, key)
        if actual != value:
            errors.append(f"{path}: {key} must be {value!r}, got {actual!r}")


def _must_contain(path: Path, text: str, values: tuple[str, ...], errors: list[str]) -> None:
    for value in values:
        if value not in text:
            errors.append(f"{path}: missing canonical value {value!r}")
    if LEGACY_TITLE in text:
        errors.append(f"{path}: legacy title remains")


def _must_not_contain(
    path: Path, text: str, values: tuple[str, ...], errors: list[str]
) -> None:
    for value in values:
        if value in text:
            errors.append(f"{path}: stale value remains {value!r}")


def _must_contain_any(
    path: Path, text: str, values: tuple[str, ...], errors: list[str]
) -> None:
    if not any(value in text for value in values):
        errors.append(f"{path}: missing one of canonical values {values!r}")


def _check_mirror(root: Path, docs_relative: str, src_relative: str, errors: list[str]) -> None:
    docs_path, src_path = root / docs_relative, root / src_relative
    docs_text, src_text = _read(docs_path, errors), _read(src_path, errors)
    if docs_text != src_text:
        errors.append(f"{src_path}: mirror differs from {docs_path}")


def validate_consumers(root: Path, cfg: dict[str, Any], errors: list[str]) -> None:
    publication = cfg.get("publication")
    required = [cfg.get(key) for key in ("title", "description", "author", "version")]
    if not isinstance(publication, dict) or not all(isinstance(value, str) for value in required):
        return
    title, description, author, version = required
    release_date = publication.get("release_date")
    last_updated = publication.get("last_updated")
    release_tag = publication.get("release_tag")
    release_status = publication.get("release_status")
    if not all(isinstance(value, str) for value in (release_date, last_updated, release_tag)):
        return

    config_path = root / "docs/_config.yml"
    config_text = _read(config_path, errors)
    expected_config = {
        "title": title,
        "description": description,
        "author": author,
        "version": version,
        "release_date": release_date,
        "last_updated": last_updated,
        "release_tag": release_tag,
    }
    if isinstance(release_status, str):
        expected_config["release_status"] = release_status
    _check_yaml_values(
        config_path,
        config_text,
        expected_config,
        errors,
    )

    index_path = root / "docs/index.md"
    index_text = _read(index_path, errors)
    _check_yaml_values(
        index_path,
        _front_matter(index_text),
        {
            "title": title,
            "description": description,
            "author": author,
            "version": version,
            "date": release_date,
            "last_modified_at": last_updated,
        },
        errors,
    )
    _must_contain(
        index_path,
        index_text,
        (title, author, version, release_date, last_updated),
        errors,
    )

    for relative in ("docs/introduction/index.md", "src/introduction/index.md"):
        path, text = root / relative, _read(root / relative, errors)
        _must_contain(path, text, (author, version, release_date, last_updated), errors)
    for relative in ("docs/afterword/index.md", "src/afterword/index.md"):
        path, text = root / relative, _read(root / relative, errors)
        _must_contain(path, text, (author, version, last_updated), errors)

    package_path = root / "package.json"
    package = _load_json(package_path, errors)
    if isinstance(package, dict):
        expected_package = {"version": version, "description": title, "author": author}
        for key, expected in expected_package.items():
            if package.get(key) != expected:
                errors.append(
                    f"{package_path}: {key} must be {expected!r}, got {package.get(key)!r}"
                )
    package_lock_path = root / "package-lock.json"
    package_lock = _load_json(package_lock_path, errors)
    if isinstance(package_lock, dict):
        packages = package_lock.get("packages")
        root_package = packages.get("") if isinstance(packages, dict) else None
        for name, actual in (
            ("version", package_lock.get("version")),
            ("packages[''].version", root_package.get("version") if isinstance(root_package, dict) else None),
        ):
            if actual != version:
                errors.append(f"{package_lock_path}: {name} must be {version!r}, got {actual!r}")

    claude_path, readme_path = root / "CLAUDE.md", root / "README.md"
    _must_contain(claude_path, _read(claude_path, errors), (title,), errors)
    readme = _read(readme_path, errors)
    _must_contain(
        readme_path,
        readme,
        (title, version, release_date, release_tag, "Web版", "公式 PDF / EPUB", "GitHub Releases"),
        errors,
    )

    changelog_path, downloads_path = root / "docs/changelog/index.md", root / "docs/downloads/index.md"
    changelog, downloads = _read(changelog_path, errors), _read(downloads_path, errors)
    _must_contain(
        changelog_path,
        changelog,
        (f"## {version} — {release_date}", release_tag, "技術内容の監査と訂正", "品質保証"),
        errors,
    )
    _must_contain(
        downloads_path,
        downloads,
        (version, release_date, release_tag, "PDF", "EPUB", "Web版", "GitHub Releases"),
        errors,
    )
    release_url = f"{RELEASE_BASE_URL}/tag/{release_tag}"
    asset_prefix = "theoretical-computer-science-textbook-"
    pdf_url = f"{RELEASE_BASE_URL}/download/{release_tag}/{asset_prefix}{release_tag}.pdf"
    epub_url = f"{RELEASE_BASE_URL}/download/{release_tag}/{asset_prefix}{release_tag}.epub"
    reader_pages = (
        (readme_path, readme),
        (changelog_path, changelog),
        (downloads_path, downloads),
    )
    if release_status == "published":
        for path, text in reader_pages:
            _must_contain(path, text, (release_url,), errors)
            _must_not_contain(path, text, STALE_PUBLISHED_COPY, errors)
        _must_contain(downloads_path, downloads, (pdf_url, epub_url), errors)
    elif release_status == "preparing":
        for path, text in reader_pages:
            _must_contain_any(path, text, STALE_PUBLISHED_COPY, errors)
            _must_not_contain(path, text, (release_url, pdf_url, epub_url), errors)
    _check_mirror(root, "docs/introduction/index.md", "src/introduction/index.md", errors)
    _check_mirror(root, "docs/afterword/index.md", "src/afterword/index.md", errors)
    _check_mirror(root, "docs/changelog/index.md", "src/changelog/index.md", errors)
    _check_mirror(root, "docs/downloads/index.md", "src/downloads/index.md", errors)

    root_changelog_path = root / "CHANGELOG.md"
    root_changelog = _read(root_changelog_path, errors)
    _must_contain(
        root_changelog_path,
        root_changelog,
        ("docs/changelog/index.md", "公開CHANGELOG", "GitHub Releases"),
        errors,
    )


def validate_workflow(root: Path, errors: list[str]) -> None:
    path = root / ".github/workflows/release-artifacts.yml"
    text = _read(path, errors)
    active = "\n".join(
        line for line in text.splitlines() if not line.lstrip().startswith("#")
    )
    if not re.search(r"(?m)^\s{4}tags:\s*\n\s{6}-\s*[\"']?v\*[\"']?\s*$", active):
        errors.append(f"{path}: missing active v* tag trigger")
    if not re.search(r"(?m)^permissions:\s*\n  contents:\s*read\s*$", active):
        errors.append(f"{path}: workflow default permissions must be contents: read")
    dispatch_match = re.search(
        r"(?ms)^  workflow_dispatch:\s*\n(?P<body>.*?)(?=^  [A-Za-z][A-Za-z_-]*:|^env:|^permissions:|^jobs:)",
        active,
    )
    dispatch = dispatch_match.group("body") if dispatch_match else ""
    for name, pattern in (
        ("release_tag input", r"(?m)^      release_tag:\s*$"),
        ("optional release_tag", r"(?m)^        required:\s*false\s*$"),
        ("string release_tag", r"(?m)^        type:\s*string\s*$"),
    ):
        if not re.search(pattern, dispatch):
            errors.append(f"{path}: workflow_dispatch is missing {name}")

    steps = re.findall(r"(?ms)^      - (.*?)(?=^      - |\Z)", active)
    step_names = [
        match.group(1)
        for step in steps
        if (match := re.match(r"name:\s*(.*?)\s*(?:\n|$)", step)) is not None
    ]
    for name in sorted(set(step_names)):
        if step_names.count(name) > 1:
            errors.append(f"{path}: duplicate step name {name!r}")

    def step_named(name: str) -> str:
        prefix = f"name: {name}"
        return next((step for step in steps if step.startswith(prefix)), "")

    build_match = re.search(r"(?ms)^  build:\s*\n(?P<body>.*?)(?=^  publish:)", active)
    build_job = build_match.group("body") if build_match else ""
    for name, pattern in (
        ("release_tag job output", r"(?m)^      release_tag:\s*\$\{\{\s*steps\.release_target\.outputs\.release_tag\s*\}\}\s*$"),
        ("artifact_label job output", r"(?m)^      artifact_label:\s*\$\{\{\s*steps\.artifact_label\.outputs\.value\s*\}\}\s*$"),
    ):
        if not re.search(pattern, build_job):
            errors.append(f"{path}: build job missing {name}")

    tooling_checkout = step_named("Checkout release tooling")
    for name, pattern in (
        ("checkout action", r"(?m)^        uses: actions/checkout@v\d+\s*$"),
        ("trusted main ref", r"(?m)^\s+ref:\s*main\s*$"),
        ("tooling path", r"(?m)^\s+path:\s*release-tooling\s*$"),
        ("credential isolation", r"(?m)^\s+persist-credentials:\s*false\s*$"),
    ):
        if not re.search(pattern, tooling_checkout):
            errors.append(f"{path}: tooling checkout missing {name}")

    target_step = step_named("Resolve release target")
    for name, pattern in (
        ("release_target id", r"(?m)^        id:\s*release_target\s*$"),
        ("safe input environment", r"inputs\.release_tag\s*\|\|\s*''"),
        ("main-only manual dispatch", r'GITHUB_EVENT_NAME\}" == "workflow_dispatch".*GITHUB_REF\}" != "refs/heads/main"'),
        ("semantic-version validation", r"\^v\[0-9\]\+\\\.\[0-9\]\+\\\.\[0-9\]\+\$"),
        ("target_ref output", r'echo "target_ref=\$\{target_ref\}" >> "\$\{GITHUB_OUTPUT\}"'),
        ("release_tag output", r'echo "release_tag=\$\{release_tag\}" >> "\$\{GITHUB_OUTPUT\}"'),
        ("artifact_source output", r'echo "artifact_source=\$\{artifact_source\}" >> "\$\{GITHUB_OUTPUT\}"'),
    ):
        if not re.search(pattern, target_step):
            errors.append(f"{path}: release-target step missing {name}")

    source_checkout = step_named("Checkout release source")
    for name, pattern in (
        ("checkout action", r"(?m)^        uses: actions/checkout@v\d+\s*$"),
        ("validated target ref", r"steps\.release_target\.outputs\.target_ref"),
        ("source path", r"(?m)^\s+path:\s*release-source\s*$"),
        ("full tag history", r"(?m)^\s+fetch-depth:\s*0\s*$"),
        ("credential isolation", r"(?m)^\s+persist-credentials:\s*false\s*$"),
    ):
        if not re.search(pattern, source_checkout):
            errors.append(f"{path}: source checkout missing {name}")

    setup_step = step_named("Setup Python")
    if not (
        re.search(r"(?m)^        uses: actions/setup-python@v\d+\s*$", setup_step)
        and re.search(r'(?m)^\s+python-version:\s*["\']?3\.12["\']?\s*$', setup_step)
    ):
        errors.append(f"{path}: deterministic Python 3.12 setup is missing")

    metadata_step = step_named("Verify canonical publication metadata and release tag")
    for name, pattern in (
        (
            "trusted checker",
            r"python3 release-tooling/scripts/check_publication_metadata\.py\s+\\\s*\n"
            r"\s+--root release-source --contract-root release-tooling",
        ),
        (
            "checked-out source commit",
            r'git -C release-source rev-parse HEAD',
        ),
        (
            "immutable tag target validation",
            r'git -C release-source rev-list -n 1 "\$\{RELEASE_TAG\}"',
        ),
        (
            "immutable source/tag equality",
            r'test "\$\{source_head\}" = "\$\{tag_head\}"',
        ),
        (
            "release tag validation",
            r'--release-tag "\$\{RELEASE_TAG\}"',
        ),
        (
            "artifact-only source validation",
            r"else\s*\n\s+python3 release-tooling/scripts/check_publication_metadata\.py\s+\\\s*\n"
            r"\s+--root release-source --contract-root release-tooling\s*\n\s+fi\s*$",
        ),
    ):
        if not re.search(pattern, metadata_step):
            errors.append(f"{path}: metadata step missing {name}")
    if "release-source/scripts/" in metadata_step:
        errors.append(f"{path}: metadata step must not execute release-source code")
    setup_index = next(
        (index for index, step in enumerate(steps) if step.startswith("name: Setup Python")),
        None,
    )
    metadata_index = next(
        (
            index
            for index, step in enumerate(steps)
            if step.startswith("name: Verify canonical publication metadata and release tag")
        ),
        None,
    )
    if setup_index is None or metadata_index is None or setup_index >= metadata_index:
        errors.append(f"{path}: Python setup must precede metadata validation")

    label_step = step_named("Resolve filesystem-safe artifact label")
    for name, pattern in (
        ("validated artifact source", r"steps\.release_target\.outputs\.artifact_source"),
        ("slash sanitization", r"ARTIFACT_SOURCE//\\//-"),
        ("artifact label output", r'echo "value=\$\{artifact_label\}" >> "\$\{GITHUB_OUTPUT\}"'),
    ):
        if not re.search(pattern, label_step):
            errors.append(f"{path}: artifact-label step missing {name}")

    source_build_step = step_named("Build offline sources (Markdown)")
    for name, pattern in (
        ("current builder", r"release-tooling/scripts/build_offline_book\.py"),
        ("tag docs root", r"--docs-root release-source/docs"),
        ("tag config", r"--config release-source/docs/book-config\.json"),
        ("EPUB preprocessing", r"--target epub --out dist/book\.epub\.md"),
        ("PDF preprocessing", r"--target pdf --out dist/book\.pdf\.md --asset-out dist"),
    ):
        if not re.search(pattern, source_build_step):
            errors.append(f"{path}: offline source build missing {name}")

    output_reference = r"steps\.artifact_label\.outputs\.value"
    for format_name in ("EPUB", "PDF"):
        build_step = step_named(f"Build {format_name}")
        suffix = format_name.lower()
        if not (
            re.search(r"(?m)^\s+pandoc\s", build_step)
            and re.search(output_reference, build_step)
            and re.search(
                rf'theoretical-computer-science-textbook-\$\{{artifact_label\}}\.{suffix}',
                build_step,
            )
        ):
            errors.append(f"{path}: Build {format_name} step lacks the safe output contract")

    upload_step = step_named("Upload workflow artifacts")
    if not re.search(r"(?m)^        uses: actions/upload-artifact@v\d+\s*$", upload_step):
        errors.append(f"{path}: workflow artifact upload step is missing")
    for suffix in ("pdf", "epub"):
        if not re.search(rf"(?m)^\s+dist/theoretical-computer-science-textbook-\*\.{suffix}\s*$", upload_step):
            errors.append(f"{path}: workflow artifact upload omits {suffix.upper()}")

    publish_match = re.search(r"(?ms)^  publish:\s*\n(?P<body>.*)\Z", active)
    publish_job = publish_match.group("body") if publish_match else ""
    for name, pattern in (
        ("build dependency", r"(?m)^    needs:\s*build\s*$"),
        ("validated release gate", r"needs\.build\.outputs\.release_tag\s*!=\s*''"),
        ("actions read permission", r"(?m)^      actions:\s*read\s*$"),
        ("contents write permission", r"(?m)^      contents:\s*write\s*$"),
    ):
        if not re.search(pattern, publish_job):
            errors.append(f"{path}: isolated publish job missing {name}")

    download_step = step_named("Download verified workflow artifacts")
    if not (
        re.search(r"(?m)^        uses: actions/download-artifact@v\d+\s*$", download_step)
        and re.search(r"(?m)^\s+name:\s*offline-artifacts\s*$", download_step)
        and re.search(r"(?m)^\s+path:\s*dist\s*$", download_step)
    ):
        errors.append(f"{path}: isolated publish job must download offline-artifacts")

    release_step = step_named("Create GitHub Release and upload assets")
    if not re.search(r"(?m)^        uses: softprops/action-gh-release@v\d+\s*$", release_step):
        errors.append(f"{path}: active GitHub Release action is missing")
    if not re.search(
        r"tag_name:\s*\$\{\{\s*needs\.build\.outputs\.release_tag\s*\}\}",
        release_step,
    ):
        errors.append(f"{path}: GitHub Release action must publish the validated tag")
    for suffix in ("pdf", "epub"):
        expected = (
            "dist/theoretical-computer-science-textbook-"
            "${{ needs.build.outputs.artifact_label }}."
            f"{suffix}"
        )
        if expected not in release_step:
            errors.append(f"{path}: GitHub Release files omit canonical {suffix.upper()} output")


def validate_builder(root: Path, errors: list[str]) -> None:
    path = root / "scripts/build_offline_book.py"
    text = _read(path, errors)
    try:
        tree = ast.parse(text, filename=str(path))
    except SyntaxError as exc:
        errors.append(f"{path}: invalid Python: {exc}")
        return

    constants = {
        node.value for node in ast.walk(tree) if isinstance(node, ast.Constant) and isinstance(node.value, str)
    }
    if "docs/book-config.json" not in constants:
        errors.append(f"{path}: canonical config default is missing")

    functions = {
        node.name: node for node in tree.body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }
    helper = functions.get("build_publication_front_matter")
    if helper is None:
        errors.append(f"{path}: publication front matter helper is missing")
    else:
        helper_source = ast.get_source_segment(text, helper) or ""
        for marker in ("date: {release_date}", "last_updated: {last_updated}"):
            if marker not in helper_source:
                errors.append(f"{path}: publication helper omits {marker!r}")

    normalizer = functions.get("normalize_math_delimiters_for_pandoc")
    if normalizer is None:
        errors.append(f"{path}: Pandoc math normalizer is missing")
    preprocess = functions.get("preprocess_markdown")
    if preprocess is None:
        errors.append(f"{path}: Markdown preprocessing entry point is missing")
    elif not any(
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "normalize_math_delimiters_for_pandoc"
        for node in ast.walk(preprocess)
    ):
        errors.append(f"{path}: Markdown preprocessing does not call the Pandoc math normalizer")

    loads_canonical_config = False
    writes_publication_front_matter = False
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            if node.func.id == "load_book_config" and node.args:
                source = ast.get_source_segment(text, node.args[0]) or ""
                loads_canonical_config |= source.replace(" ", "") == "Path(args.config)"
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            if node.func.attr == "write_text" and node.args:
                expression = ast.get_source_segment(text, node.args[0]) or ""
                writes_publication_front_matter |= (
                    "build_publication_front_matter(cfg)" in expression
                    and "combined_text" in expression
                )
    if not loads_canonical_config:
        errors.append(f"{path}: main path does not load args.config")
    if not writes_publication_front_matter:
        errors.append(f"{path}: output does not prepend canonical publication metadata")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="repository root")
    parser.add_argument(
        "--contract-root",
        type=Path,
        help="trusted root containing the release workflow and offline builder",
    )
    parser.add_argument("--release-tag", help="tag supplied by the release workflow")
    args = parser.parse_args(argv)
    root, errors = args.root.resolve(), []
    contract_root = args.contract_root.resolve() if args.contract_root else root
    cfg = validate_config(root, errors)
    if cfg is not None:
        publication = cfg.get("publication")
        canonical_tag = publication.get("release_tag") if isinstance(publication, dict) else None
        release_status = (
            publication.get("release_status") if isinstance(publication, dict) else None
        )
        # Immutable release sources created before this field was introduced remain
        # retryable. Current branch validation must always declare the reader state.
        if release_status is None and args.release_tag is None:
            errors.append(
                "publication.release_status: required for current publication state"
            )
        if args.release_tag is not None and args.release_tag != canonical_tag:
            errors.append(
                f"--release-tag {args.release_tag!r} does not match canonical {canonical_tag!r}"
            )
        validate_consumers(root, cfg, errors)
    validate_workflow(contract_root, errors)
    validate_builder(contract_root, errors)
    if errors:
        print("publication metadata check failed:", file=sys.stderr)
        print("\n".join(f"- {error}" for error in errors), file=sys.stderr)
        return 1
    print("OK: publication metadata is canonical and release contracts are synchronized")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
