# Operating Model

This operating model treats a local AI workspace as a managed environment, not
as a loose folder of scripts and generated files.

## Workspace Role

The workspace root coordinates:

- reusable tools;
- project directories;
- pipeline implementations;
- templates;
- governance documentation;
- Git decision reports.

The root should stay small and managerial. Concrete work should live inside a
project directory.

## Recommended Layout

```text
workspace-root/
  docs/
  templates/
  projects/
    project-name/
      README.md
      data/
        raw/
        working/
        output/
      pipelines/
        pipeline-name/
          README.md
          scripts/
          configs/
          runs/
  workspace_guard/
  pipeline_registry.md
```

## Asset Classes

### Durable Assets

Put these in Git:

- source code;
- stable configs;
- templates;
- governance docs;
- prompt or skill rules;
- small sanitized examples;
- README files and project indexes.

### Review Assets

Review before committing:

- raw data;
- spreadsheets;
- PDFs;
- Word documents;
- exported knowledge notes from private source material;
- business or client context;
- large binary files.

### Local Artifacts

Keep these out of normal commits:

- generated outputs;
- run artifacts;
- dependency folders;
- caches;
- temporary transfer folders;
- local credentials;
- API keys;
- rendered previews.

## Git Workflow

1. Run the scanner.
2. Read the decision summary.
3. Stage only understood paths.
4. Keep unrelated projects in separate commits.
5. Write commit messages that explain why a project asset entered history.
6. Use force-add only for intentionally archived review/block assets.

## Practical Principle

Git history should explain the reusable structure and durable work product of
the workspace. It should not become a storage dump for everything produced
during AI-assisted work.

