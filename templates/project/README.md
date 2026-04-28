# Project Name

## Purpose

Describe what this project owns and what should not be stored here.

## Directory Map

| Path | Purpose |
| --- | --- |
| `data/raw/` | Immutable source inputs. |
| `data/working/` | Intermediate working files. |
| `data/output/` | Final outputs and deliverables. |
| `docs/` | Project-specific documentation. |
| `pipelines/` | Repeatable pipeline implementations. |

## Active Pipelines

| Pipeline | Purpose | Registry |
| --- | --- | --- |
| `_none_yet_` |  | `../../pipeline_registry.md` |

## Rules

- Do not put project files at workspace root.
- Do not overwrite raw inputs.
- Register repeatable pipelines in the workspace registry.
- Keep generated outputs out of normal commits unless intentionally archived.

