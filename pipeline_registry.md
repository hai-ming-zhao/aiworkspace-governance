# Pipeline Registry

This file indexes repeatable pipelines in the workspace.

## Active Pipelines

| Pipeline | Project | Entrypoint | Status |
| --- | --- | --- | --- |
| `sample_pipeline` | `examples/sample_workspace/projects/sample_project` | `pipelines/sample_pipeline/scripts/run.py` | example |

## Registry Rules

- Add reusable workflows here before treating them as active.
- Do not register one-off scripts unless they become repeatable.
- Keep entrypoints relative to the workspace root.
- Record retired pipelines as `retired` instead of silently deleting them.

## Pipeline Record Template

```text
Pipeline:
Project:
Entrypoint:
Inputs:
Outputs:
Run directory:
Status:
Last verified:
Notes:
```

