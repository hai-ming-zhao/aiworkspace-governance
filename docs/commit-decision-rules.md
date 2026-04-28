# Commit Decision Rules

The scanner classifies changed paths before staging. It uses path patterns,
file names, and extensions to assign one of three decisions.

## ALLOW

Use `ALLOW` for paths that are structurally safe to consider for normal staging.

Examples:

- `.md`
- `.py`
- `.js`
- `.json`
- `.yaml`
- `README.md`
- `docs/`
- `templates/`
- `scripts/`
- stable config files

`ALLOW` is not automatic approval. It means the path does not match known risk
patterns.

## REVIEW

Use `REVIEW` for paths that may belong in Git, but require human judgment.

Examples:

- `raw/`
- `data/`
- `original/`
- `.pdf`
- `.docx`
- `.xlsx`
- `.csv`
- `.jsonl`
- business or personal context directories

These files may be durable evidence or useful examples, but they may also be
private, large, externally licensed, or better stored outside Git.

## BLOCK

Use `BLOCK` for paths that should not be committed by default.

Examples:

- `node_modules/`
- `__pycache__/`
- `.pytest_cache/`
- `.venv/`
- `.env`
- `outputs/`
- `output/`
- `runs/` artifacts except `runs/README.md`
- `*_render/`
- generated scan reports

Only force-add a blocked path when the commit message or project README explains
why it is intentionally archived.

## Why This Is Advisory

The scanner does not replace human judgment. It gives a repeatable first pass
that catches common AI-workspace mistakes before files enter Git history.

