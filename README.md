# AI Workspace Governance

A lightweight Git governance pattern for local AI-assisted workspaces.

This project helps solo builders, researchers, consultants, and AI-heavy
knowledge workers keep local workspace repositories clean. It separates durable
assets from generated outputs, raw data, dependencies, caches, and sensitive
files before they enter Git history.

## What It Provides

- A generic workspace operating model.
- A pre-commit review scanner with `ALLOW`, `REVIEW`, and `BLOCK` decisions.
- Default rules for generated files, binary data, raw inputs, local secrets, and
  dependency folders.
- Project and pipeline templates.
- A sanitized example workspace.

## Why This Exists

AI-assisted work creates many file types quickly:

- scripts and prompts;
- pipeline configs;
- markdown notes;
- spreadsheet inputs;
- generated reports;
- rendered previews;
- temporary run artifacts;
- local model or API outputs.

Plain `git status` does not explain which files are durable project assets and
which files are local artifacts. This repo adds a small governance layer before
`git add`.

## Quick Start

Run the scanner against any Git workspace:

```powershell
python .\workspace_guard\scan.py --root "C:\path\to\workspace"
```

Write Markdown and JSON reports:

```powershell
python .\workspace_guard\scan.py --root "C:\path\to\workspace" --write --json
```

Scan the included example workspace:

```powershell
python .\workspace_guard\scan.py --root .\examples\sample_workspace
```

## Decisions

The scanner assigns each changed path one decision:

| Decision | Meaning |
| --- | --- |
| `ALLOW` | Structurally safe to consider for normal staging. |
| `REVIEW` | Needs human confirmation before staging. |
| `BLOCK` | Should not be committed by default. |

These are advisory decisions. The tool does not stage, commit, delete, or push
anything.

## Suggested Repository Structure

```text
workspace-root/
  docs/
  templates/
  projects/
    project-a/
      README.md
      data/
      pipelines/
  workspace_guard/
  pipeline_registry.md
```

Use Git for durable code, documentation, rules, configs, and small sanitized
examples. Keep raw private data, generated outputs, and large binaries outside
normal commits.

## Documentation

- [Operating Model](docs/operating-model.md)
- [Commit Decision Rules](docs/commit-decision-rules.md)
- [Publishing Checklist](docs/publishing-checklist.md)

## License

MIT License. See [LICENSE](LICENSE).

