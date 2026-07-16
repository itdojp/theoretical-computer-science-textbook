from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[2]


def test_svg_lint_scripts_have_valid_bash_syntax() -> None:
    for relative in ("scripts/svg-lint.sh", "scripts/svg-lint-a11y.sh"):
        subprocess.run(
            ["bash", "-n", str(ROOT / relative)],
            check=True,
            cwd=ROOT,
        )
