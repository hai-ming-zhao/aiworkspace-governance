# Contributing

Thanks for improving AI Workspace Governance.

## Development

Run the test suite before submitting changes:

```powershell
python -m pytest -q
```

Rule changes should include focused tests in `tests/test_scan_rules.py`.

## Rule Changes

The scanner is intentionally conservative and read-only. It must not stage,
commit, delete, or push files.

When changing classification behavior, update the documentation if the public
meaning of `ALLOW`, `REVIEW`, `BLOCK`, `--include-excluded`, or
`--fail-on-block` changes.

## Publishing Hygiene

Do not commit local raw data, generated reports, dependency folders, cache
directories, or private workspace experiments. Use small sanitized examples
when test data is needed.
