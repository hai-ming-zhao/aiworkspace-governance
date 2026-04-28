# AI Workspace Governance

A read-only Git change classifier for AI-assisted local workspaces.

This project helps solo builders, researchers, consultants, and AI-heavy
knowledge workers keep local workspace repositories clean. It separates durable
assets from generated outputs, raw data, dependencies, caches, and sensitive
files before they enter Git history.

The GitHub repository is `aiworkspace-governance`; the Python project name is
`ai-workspace-governance`.

## What It Provides

- A generic workspace operating model.
- A read-only pre-staging scanner with `ALLOW`, `REVIEW`, and `BLOCK`
  decisions.
- Default rules for generated files, binary data, raw inputs, local secrets, and
  dependency folders.
- Project and pipeline templates.
- A sanitized example workspace.

## What It Is Not

- It is not a secret scanner.
- It is not a compliance, legal, or data-governance system.
- It does not decide whether a file is safe to publish.
- It does not stage, commit, delete, push, or rewrite files.

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

Or run it as a Python module:

```powershell
python -m workspace_guard.scan --root "C:\path\to\workspace"
```

Write Markdown and JSON reports:

```powershell
python .\workspace_guard\scan.py --root "C:\path\to\workspace" --write --json
```

Show generated, cache, and dependency paths that are hidden by default:

```powershell
python .\workspace_guard\scan.py --root "C:\path\to\workspace" --include-excluded
```

Fail with exit code `1` when a `BLOCK` decision is found:

```powershell
python .\workspace_guard\scan.py --root "C:\path\to\workspace" --fail-on-block
```

Scan the included example workspace:

```powershell
python .\workspace_guard\scan.py --root .\examples\sample_workspace
```

Example output:

```text
## Decision Summary

- `ALLOW`: 4
- `REVIEW`: 2
- `BLOCK`: 1

## Project Changes

- `ALLOW` `modified` `docs/project-note.md`
- `REVIEW` `untracked` `data/raw/source.xlsx` [review-data-or-binary]
- `BLOCK` `untracked` `outputs/report.pdf` [review-generated-or-cache]
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

## Disclaimer

This project provides general workflow and repository-governance guidance for
AI-assisted local workspaces. It is not legal, security, compliance, or
data-governance advice.

The scanner uses path, filename, and extension heuristics. It cannot guarantee
that a repository is free of secrets, private data, copyrighted material, or
sensitive information. Review all files manually before publishing or pushing to
a remote repository.

## License

MIT License. See [LICENSE](LICENSE).
