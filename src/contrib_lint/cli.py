from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path

DEFAULT_FILES = [
    "README.md",
    "CONTRIBUTING.md",
    "SECURITY.md",
    "LICENSE",
    ".gitignore",
]
DEFAULT_CONTRIBUTING_SECTIONS = ["contribut", "test", "pull request"]


@dataclass(frozen=True)
class Finding:
    code: str
    severity: str
    path: str
    detail: str
    remediation: str


def load_config(path: Path | None) -> dict:
    if path is None:
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"config is not valid JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError("config must be a JSON object")
    return data


def _configured_list(config: dict, key: str, default: list[str]) -> list[str]:
    value = config.get(key, default)
    if not isinstance(value, list) or not all(isinstance(item, str) and item for item in value):
        raise ValueError(f"config field {key!r} must be a non-empty string list")
    return value


def scan(root: Path, config: dict | None = None) -> list[Finding]:
    root = root.resolve()
    config = config or {}
    required_files = _configured_list(config, "required_files", DEFAULT_FILES)
    required_sections = [item.lower() for item in _configured_list(config, "contributing_sections", DEFAULT_CONTRIBUTING_SECTIONS)]
    findings: list[Finding] = []

    for relative in required_files:
        candidate = root / relative
        if not candidate.is_file():
            findings.append(Finding(
                "MISSING_FILE",
                "warning",
                relative,
                f"required repository file is missing: {relative}",
                f"Add {relative} or override required_files in a project config.",
            ))

    readme = root / "README.md"
    if readme.is_file():
        text = readme.read_text(encoding="utf-8", errors="replace")
        lowered = text.lower()
        if len(text.strip()) < 200:
            findings.append(Finding(
                "SHORT_README",
                "warning",
                "README.md",
                "README is shorter than 200 characters and may not explain setup or scope.",
                "Add a concise purpose, quick start, use cases, and limitations.",
            ))
        if not any(marker in lowered for marker in ("quick start", "quickstart", "getting started", "installation")):
            findings.append(Finding(
                "MISSING_QUICKSTART",
                "warning",
                "README.md",
                "README does not contain a recognizable setup section.",
                "Add a copy-pasteable quick start that works from a clean checkout.",
            ))

    contributing = root / "CONTRIBUTING.md"
    if contributing.is_file():
        text = contributing.read_text(encoding="utf-8", errors="replace").lower()
        for section in required_sections:
            if section not in text:
                findings.append(Finding(
                    "MISSING_CONTRIBUTING_GUIDANCE",
                    "warning",
                    "CONTRIBUTING.md",
                    f"contribution guide does not mention {section!r}.",
                    "Document the expected workflow so contributors can self-check before opening a PR.",
                ))

    pr_template = root / ".github" / "pull_request_template.md"
    legacy_template = root / ".github" / "PULL_REQUEST_TEMPLATE.md"
    template_directory = root / ".github" / "PULL_REQUEST_TEMPLATE"
    has_directory_template = template_directory.is_dir() and any(
        path.is_file() and path.suffix.lower() == ".md"
        for path in template_directory.iterdir()
    )
    if not pr_template.is_file() and not legacy_template.is_file() and not has_directory_template:
        findings.append(Finding(
            "MISSING_PR_TEMPLATE",
            "info",
            ".github/pull_request_template.md",
            "no pull-request template was found.",
            "Add a lightweight checklist for tests, docs, security impact, and limitations.",
        ))

    return findings


def render_text(root: Path, findings: list[Finding]) -> str:
    lines = [f"contrib-lint: {root}"]
    if not findings:
        return "\n".join(lines + ["PASS  no contribution-quality findings"]) + "\n"
    for finding in findings:
        lines.append(f"{finding.severity.upper():7} {finding.code:28} {finding.path} — {finding.detail}")
        lines.append(f"         Remediation: {finding.remediation}")
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Offline repository contribution-quality linter")
    parser.add_argument("path", nargs="?", type=Path, default=Path("."))
    parser.add_argument("--config", type=Path, help="optional JSON config with required_files and contributing_sections")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    parser.add_argument("--fail-on", choices=("error", "warning", "never"), default="warning")
    args = parser.parse_args(argv)
    root = args.path.resolve()
    if not root.is_dir():
        parser.error(f"path is not a directory: {root}")
    try:
        findings = scan(root, load_config(args.config))
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    if args.format == "json":
        print(json.dumps({"path": str(root), "findings": [asdict(item) for item in findings]}, indent=2))
    else:
        print(render_text(root, findings), end="")
    if args.fail_on == "never":
        return 0
    if args.fail_on == "warning" and any(item.severity in {"warning", "error"} for item in findings):
        return 1
    if args.fail_on == "error" and any(item.severity == "error" for item in findings):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
