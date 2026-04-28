# Pipeline Name

## Purpose

Describe the repeatable workflow and its owner project.

## Entrypoint

```powershell
python -B scripts\<entrypoint>.py --help
```

## Inputs

- Input type:
- Required columns/fields:
- Source directory:

## Outputs

- Output type:
- Output directory:
- Status/error fields:

## Standard Run Flow

1. Inspect inputs.
2. Run a dry run or validation pass.
3. Run the full pipeline.
4. Validate outputs.
5. Record run notes under `runs/<timestamp>-<short-name>/`.

## Key Files

| Path | Purpose |
| --- | --- |
| `scripts/` | Executable scripts. |
| `configs/` | Stable configuration. |
| `docs/` | User-facing docs and examples. |
| `runs/` | Per-run artifacts and notes. |

