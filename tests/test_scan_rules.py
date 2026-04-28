from workspace_guard.scan import classify_path, decide_path, load_config


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

