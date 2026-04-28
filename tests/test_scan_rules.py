from workspace_guard.scan import (
    Change,
    classify_path,
    decide_path,
    load_config,
    main,
    parse_status_line,
    pattern_matches,
    visible_changes,
)


def test_generated_output_is_blocked():
    config = load_config()
    path = "projects/example/output/result.txt"
    flags = classify_path(path, config)
    assert decide_path(path, flags, config) == "BLOCK"


def test_raw_readme_is_allowed():
    config = load_config()
    path = "projects/example/data/raw/README.md"
    flags = classify_path(path, config)
    assert decide_path(path, flags, config) == "ALLOW"


def test_binary_data_requires_review():
    config = load_config()
    path = "projects/example/data/source.xlsx"
    flags = classify_path(path, config)
    assert decide_path(path, flags, config) == "REVIEW"


def test_output_directory_matches_path_segment_only():
    assert pattern_matches("projects/example/outputs/result.txt", "outputs/")
    assert not pattern_matches("projects/example/myoutputs/result.txt", "outputs/")


def test_data_directory_does_not_match_metadata_or_database():
    assert pattern_matches("projects/example/data/source.txt", "data/")
    assert not pattern_matches("projects/example/metadata.json", "data/")
    assert not pattern_matches("projects/example/database/source.txt", "data/")


def test_sensitive_names_are_split_between_block_and_review():
    config = load_config()

    env_flags = classify_path(".env", config)
    assert decide_path(".env", env_flags, config) == "BLOCK"

    env_example_flags = classify_path(".env.example", config)
    assert decide_path(".env.example", env_example_flags, config) == "REVIEW"

    token_flags = classify_path("docs/token_notes.md", config)
    assert decide_path("docs/token_notes.md", token_flags, config) == "REVIEW"

    password_flags = classify_path("docs/password_policy.md", config)
    assert decide_path("docs/password_policy.md", password_flags, config) == "REVIEW"


def test_unknown_top_level_project_requires_review_when_configured():
    config = {**load_config(), "top_level_projects": ["docs", "workspace_guard"]}

    change = parse_status_line("?? projects/new_project/README.md", config)

    assert change.decision == "REVIEW"
    assert "review-unknown-project" in change.flags


def test_visible_changes_hide_excluded_paths_by_default():
    changes = [
        Change(status="??", label="untracked", path="docs/note.md", project="docs"),
        Change(status="??", label="untracked", path="node_modules/pkg/index.js", project="node_modules", excluded=True),
    ]

    visible, hidden = visible_changes(changes, include_excluded=False)
    included, included_hidden = visible_changes(changes, include_excluded=True)

    assert [change.path for change in visible] == ["docs/note.md"]
    assert hidden == 1
    assert [change.path for change in included] == ["docs/note.md", "node_modules/pkg/index.js"]
    assert included_hidden == 0


def test_fail_on_block_returns_nonzero(monkeypatch):
    monkeypatch.setattr("workspace_guard.scan.run_git_status", lambda root: ["?? output/result.txt"])

    assert main(["--fail-on-block"]) == 1
