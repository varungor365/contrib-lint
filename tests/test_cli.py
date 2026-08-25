from pathlib import Path

from contrib_lint.cli import scan


def make_repo(root: Path) -> None:
    (root / "README.md").write_text("# Demo\n\n## Quick start\n\n" + "x" * 220, encoding="utf-8")
    (root / "CONTRIBUTING.md").write_text("# Contributing\n\n## Contributions\n\n## Tests\n\n## Pull requests\n", encoding="utf-8")
    (root / "SECURITY.md").write_text("# Security\n", encoding="utf-8")
    (root / "LICENSE").write_text("MIT\n", encoding="utf-8")
    (root / ".gitignore").write_text(".venv/\n", encoding="utf-8")
    (root / ".github").mkdir()
    (root / ".github" / "pull_request_template.md").write_text("- [ ] Tests\n", encoding="utf-8")


def test_complete_repository_has_no_findings(tmp_path: Path):
    make_repo(tmp_path)
    assert scan(tmp_path) == []


def test_missing_guidance_is_reported(tmp_path: Path):
    (tmp_path / "README.md").write_text("# Demo\n\n## Quick start\n\n" + "x" * 220, encoding="utf-8")
    findings = scan(tmp_path)
    codes = {item.code for item in findings}
    assert "MISSING_FILE" in codes
    assert "MISSING_PR_TEMPLATE" in codes


def test_config_can_require_project_specific_files(tmp_path: Path):
    (tmp_path / "README.md").write_text("# Demo\n\n## Installation\n\n" + "x" * 220, encoding="utf-8")
    findings = scan(tmp_path, {"required_files": ["README.md", "ARCHITECTURE.md"], "contributing_sections": ["review"]})
    assert any(item.path == "ARCHITECTURE.md" for item in findings)


def test_short_readme_and_missing_quickstart_are_actionable(tmp_path: Path):
    (tmp_path / "README.md").write_text("# Demo\n", encoding="utf-8")
    findings = scan(tmp_path)
    codes = {item.code for item in findings}
    assert {"SHORT_README", "MISSING_QUICKSTART"} <= codes
