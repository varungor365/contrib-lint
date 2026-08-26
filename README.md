# contrib-lint

**Offline repository contribution-quality checks for `CONTRIBUTING.md`, pull-request templates, README quick starts, security guidance, licenses, and project hygiene.**

`contrib-lint` helps maintainers make contribution expectations visible before a pull request arrives. It reads local files only, reports missing or incomplete guidance, supports stable JSON for CI or issue templates, and never edits a repository or sends source code over the network.

## Why this exists

GitHub maintainers report that low-quality or abandoned contributions create a substantial review burden, especially when submissions do not follow project guidelines. A small, deterministic preflight check can turn implicit expectations into actionable feedback without attempting to judge a contributor or detect whether code was written by an AI.

## Three-minute quick start

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install contrib-lint
cd path/to/your/repository
contrib-lint .
```

The default command is read-only and exits with status `1` when warnings are found. To inspect the result without failing a pipeline:

```bash
contrib-lint . --format json --fail-on never
```

To use it in CI:

```yaml
- name: Check contribution guidance
  run: |
    python -m pip install contrib-lint
    contrib-lint . --fail-on warning
```

## What it checks

| Check | Default behavior |
|---|---|
| Required repository files | Warns when `README.md`, `CONTRIBUTING.md`, `SECURITY.md`, `LICENSE`, or `.gitignore` is missing. |
| README onboarding | Warns when the README is very short or lacks a recognizable quick-start section. |
| Contribution guidance | Warns when `CONTRIBUTING.md` does not mention contributions, tests, or pull requests. |
| Pull-request template | Reports an informational finding when no template exists under `.github/`, including the directory form `.github/PULL_REQUEST_TEMPLATE/*.md`. |
| Custom policy | Accepts a local JSON file for project-specific required files and contribution terms. |

## Example

The repository includes a complete fixture under [`examples/repository`](examples/repository). Run:

```bash
contrib-lint examples/repository --fail-on warning
contrib-lint examples/repository --format json --fail-on never
```

A project-specific policy can be supplied without modifying the tool:

```json
{
  "required_files": ["README.md", "ARCHITECTURE.md", "SECURITY.md"],
  "contributing_sections": ["review", "tests"]
}
```

```bash
contrib-lint . --config contrib-lint.json
```

## Safe defaults

The linter performs local filesystem reads only. It does not clone repositories, call GitHub, inspect commit authorship, infer whether code was AI-generated, execute project code, install dependencies, or print file contents. It reports the path and remediation text, not secrets or source snippets.

## Limitations

A present file is not proof that its instructions are accurate, complete, or safe. The default checks are intentionally shallow and language-agnostic. They do not validate links, run installation commands, assess code quality, or replace human review, CI, security scanning, or repository branch protections. Custom policies are trusted input and should be reviewed like any other project configuration.

## Development

```bash
git clone https://github.com/varungor365/contrib-lint
cd contrib-lint
python -m pip install -e '.[test]'
pytest -q
python -m compileall -q src tests
```

## Why star this repository?

Star `contrib-lint` if you maintain open-source repositories, want contribution expectations checked locally or in CI, or prefer transparent repository hygiene checks over opaque contributor scoring.

## License

MIT. See [`LICENSE`](LICENSE).
