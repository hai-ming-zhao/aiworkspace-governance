#!/usr/bin/env python
"""Read-only Git declaration scanner for AI-assisted workspaces."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import subprocess
import sys
from dataclasses import dataclass, field
from typing import Iterable


STATUS_LABELS = {
    "??": "untracked",
    " M": "modified",
    "M ": "modified-index",
    "MM": "modified-index-worktree",
    "A ": "added-index",
    "AM": "added-index-modified",
    " D": "deleted",
    "D ": "deleted-index",
    "R ": "renamed-index",
    "C ": "copied-index",
}


@dataclass
class Change:
    status: str
    label: str
    path: str
    project: str
    decision: str = "ALLOW"
    excluded: bool = False
    flags: list[str] = field(default_factory=list)


def package_dir() -> pathlib.Path:
    return pathlib.Path(__file__).resolve().parent


def load_config(path: str | None = None) -> dict:
    config_path = pathlib.Path(path) if path else package_dir() / "default_rules.json"
    with config_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def run_git_status(root: pathlib.Path) -> list[str]:
    command = ["git", "-c", "core.quotePath=false", "-C", str(root), "status", "--porcelain=v1", "-uall"]
    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if result.returncode != 0:
        sys.stderr.write(result.stderr)
        raise SystemExit(result.returncode)
    return [line for line in result.stdout.splitlines() if line.strip()]


def normalize_path(raw_path: str) -> str:
    path = raw_path.strip()
    if " -> " in path:
        path = path.split(" -> ", 1)[1]
    if path.startswith('"') and path.endswith('"'):
        path = path[1:-1]
    return path.replace("\\", "/")


def project_for(path: str) -> str:
    parts = path.split("/", 1)
    return parts[0] if len(parts) > 1 else "."


def path_parts(path: str) -> list[str]:
    normalized = path.lower().replace("\\", "/")
    return [part for part in normalized.split("/") if part]


def has_part_sequence(parts: list[str], targets: list[str]) -> bool:
    if not targets:
        return False
    end = len(parts) - len(targets) + 1
    return any(parts[index : index + len(targets)] == targets for index in range(max(end, 0)))


def pattern_matches(path: str, pattern: str) -> bool:
    parts = path_parts(path)
    path_text = "/".join(parts)
    normalized = pattern.lower().replace("\\", "/").strip()
    if not normalized:
        return False

    directory_pattern = normalized.endswith("/")
    normalized = normalized.strip("/")
    targets = [part for part in normalized.split("/") if part]

    if directory_pattern:
        if len(targets) == 1 and targets[0].startswith("_"):
            return any(part == targets[0] or part.endswith(targets[0]) for part in parts)
        return has_part_sequence(parts, targets)

    if "/" in normalized:
        return path_text == normalized or path_text.startswith(f"{normalized}/") or path_text.startswith(normalized)

    if normalized in parts:
        return True
    return normalized.startswith("_") and any(part.endswith(normalized) for part in parts)


def path_allowed(path: str, config: dict) -> bool:
    normalized_path = path.lower().replace("\\", "/")
    allowed_patterns = [item.lower().replace("\\", "/") for item in config.get("allow_path_patterns", [])]
    return any(normalized_path == pattern or normalized_path.endswith(f"/{pattern}") for pattern in allowed_patterns)


def is_allowlisted(path: str, config: dict) -> bool:
    return path_allowed(path, config)


def sensitive_kind(name: str, config: dict) -> str | None:
    lowered = name.lower()
    block_patterns = config.get("sensitive_block_name_patterns", config.get("sensitive_name_patterns", []))
    review_patterns = config.get("sensitive_review_name_patterns", [])
    template_suffixes = (".example", ".sample", ".template", ".dist")

    if lowered.startswith(".env.") and lowered.endswith(template_suffixes):
        return "review"

    for pattern in block_patterns:
        normalized = pattern.lower()
        if lowered == normalized:
            return "block"
        if normalized == ".env" and lowered.startswith(".env."):
            return "block"
        if normalized != ".env" and normalized in lowered:
            return "block"

    for pattern in review_patterns:
        if pattern.lower() in lowered:
            return "review"

    return None


def classify_path(path: str, config: dict) -> list[str]:
    flags: list[str] = []
    allowed = path_allowed(path, config)

    if not allowed:
        for pattern in config.get("generated_path_patterns", []):
            if pattern_matches(path, pattern):
                flags.append("review-generated-or-cache")
                break

    name = pathlib.PurePosixPath(path).name.lower()
    kind = sensitive_kind(name, config)
    if kind == "block":
        flags.append("block-sensitive")
    elif kind == "review":
        flags.append("review-sensitive")

    suffix = pathlib.PurePosixPath(path).suffix.lower()
    if suffix in set(config.get("data_extensions", [])):
        flags.append("review-data-or-binary")

    return flags


def decide_path(path: str, flags: list[str], config: dict) -> str:
    allowed = path_allowed(path, config)

    if "block-sensitive" in flags:
        return "BLOCK"

    if not allowed:
        for pattern in config.get("block_path_patterns", []):
            if pattern_matches(path, pattern):
                return "BLOCK"

    if allowed:
        return "ALLOW"

    if "review-data-or-binary" in flags or "review-sensitive" in flags:
        return "REVIEW"

    for pattern in config.get("review_path_patterns", []):
        if pattern_matches(path, pattern):
            return "REVIEW"

    return "ALLOW"


def apply_project_rules(change: Change, config: dict) -> None:
    known_projects = {project.lower() for project in config.get("top_level_projects", [])}
    if known_projects and change.project.lower() not in known_projects:
        change.flags.append("review-unknown-project")
        if change.decision == "ALLOW":
            change.decision = "REVIEW"


def parse_status_line(line: str, config: dict) -> Change:
    status = line[:2]
    path = normalize_path(line[3:])
    flags = classify_path(path, config)
    change = Change(
        status=status,
        label=STATUS_LABELS.get(status, status.strip() or "changed"),
        path=path,
        project=project_for(path),
        flags=flags,
        decision=decide_path(path, flags, config),
    )
    apply_project_rules(change, config)
    change.excluded = should_exclude_path(path, config)
    return change


def should_exclude_path(path: str, config: dict) -> bool:
    return any(pattern_matches(path, pattern) for pattern in config.get("exclude_path_patterns", []))


def collect_changes(root: pathlib.Path, config: dict) -> list[Change]:
    return [parse_status_line(line, config) for line in run_git_status(root)]


def group_by_project(changes: Iterable[Change]) -> dict[str, list[Change]]:
    grouped: dict[str, list[Change]] = {}
    for change in changes:
        grouped.setdefault(change.project, []).append(change)
    return dict(sorted(grouped.items(), key=lambda item: item[0].lower()))


def summarize(changes: list[Change], excluded_hidden: int = 0) -> dict:
    grouped = group_by_project(changes)
    by_status: dict[str, int] = {}
    by_decision: dict[str, int] = {}
    flagged = 0
    for change in changes:
        by_status[change.label] = by_status.get(change.label, 0) + 1
        by_decision[change.decision] = by_decision.get(change.decision, 0) + 1
        if change.flags:
            flagged += 1
    return {
        "total": len(changes),
        "excluded_hidden": excluded_hidden,
        "projects": len(grouped),
        "flagged": flagged,
        "by_status": dict(sorted(by_status.items())),
        "by_decision": dict(sorted(by_decision.items())),
    }


def render_markdown(
    root: pathlib.Path,
    changes: list[Change],
    project_filter: str | None,
    excluded_hidden: int = 0,
) -> str:
    now = dt.datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %z")
    summary = summarize(changes, excluded_hidden)
    grouped = group_by_project(changes)
    lines = [
        "# Git Declaration Report",
        "",
        f"- Root: `{root}`",
        f"- Generated: `{now}`",
        f"- Project filter: `{project_filter or 'all'}`",
        f"- Total changes: `{summary['total']}`",
        f"- Hidden excluded changes: `{summary['excluded_hidden']}`",
        f"- Changed projects: `{summary['projects']}`",
        f"- Flagged paths: `{summary['flagged']}`",
        "",
        "## Decision Summary",
        "",
    ]

    if summary["by_decision"]:
        for decision, count in summary["by_decision"].items():
            lines.append(f"- `{decision}`: {count}")
    else:
        lines.append("- clean")

    lines.extend(["", "## Status Summary", ""])
    if summary["by_status"]:
        for label, count in summary["by_status"].items():
            lines.append(f"- `{label}`: {count}")
    else:
        lines.append("- clean")

    lines.extend(
        [
            "",
            "## Review Rules",
            "",
            "- This report is read-only and does not stage or commit anything.",
            "- `ALLOW` means the path is structurally safe to consider for normal staging.",
            "- `REVIEW` means data, binary, raw source, or project-sensitive context needs human confirmation.",
            "- `BLOCK` means generated output, cache, dependency, local secret, or report artifact should not be committed by default.",
            "- Dependency folders and generated declaration reports are hidden by default; use `--include-excluded` to show them.",
            "",
            "## Project Changes",
            "",
        ]
    )

    if not grouped:
        lines.append("No Git changes detected.")
        return "\n".join(lines) + "\n"

    for project, items in grouped.items():
        lines.append(f"### `{project}`")
        lines.append("")
        for change in items:
            flag_text = f" [{', '.join(change.flags)}]" if change.flags else ""
            lines.append(f"- `{change.decision}` `{change.label}` `{change.path}`{flag_text}")
        lines.append("")

    return "\n".join(lines)


def render_json(
    root: pathlib.Path,
    changes: list[Change],
    project_filter: str | None,
    excluded_hidden: int = 0,
) -> dict:
    return {
        "root": str(root),
        "generated_at": dt.datetime.now().astimezone().isoformat(),
        "project_filter": project_filter,
        "summary": summarize(changes, excluded_hidden),
        "changes": [
            {
                "status": change.status,
                "label": change.label,
                "path": change.path,
                "project": change.project,
                "decision": change.decision,
                "excluded": change.excluded,
                "flags": change.flags,
            }
            for change in changes
        ],
    }


def report_base_path(output_dir: pathlib.Path) -> pathlib.Path:
    timestamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    return output_dir / f"git_declaration_{timestamp}"


def filter_changes(changes: list[Change], project: str | None) -> list[Change]:
    if not project:
        return changes
    return [change for change in changes if change.project.lower() == project.lower()]


def visible_changes(changes: list[Change], include_excluded: bool) -> tuple[list[Change], int]:
    if include_excluded:
        return changes, 0
    visible = [change for change in changes if not change.excluded]
    return visible, len(changes) - len(visible)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Track Git declaration status for an AI workspace.")
    parser.add_argument("--root", default=".", help="Git repository root to scan.")
    parser.add_argument("--config", help="Optional JSON rule config.")
    parser.add_argument("--project", help="Only include one top-level project.")
    parser.add_argument("--write", action="store_true", help="Write Markdown report.")
    parser.add_argument("--json", action="store_true", help="Also write JSON when --write is used.")
    parser.add_argument("--fail-on-block", action="store_true", help="Exit with code 1 if any BLOCK decision is found.")
    parser.add_argument("--include-excluded", action="store_true", help="Show dependency, cache, and generated report paths.")
    parser.add_argument("--output-dir", default="reports", help="Report output directory.")
    parser.add_argument("--quiet", action="store_true", help="Only print output paths when writing.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    root = pathlib.Path(args.root).resolve()
    config = load_config(args.config)
    changes = filter_changes(collect_changes(root, config), args.project)
    changes, excluded_hidden = visible_changes(changes, args.include_excluded)
    markdown = render_markdown(root, changes, args.project, excluded_hidden)

    if args.write:
        output_dir = pathlib.Path(args.output_dir)
        if not output_dir.is_absolute():
            output_dir = root / output_dir
        output_dir.mkdir(parents=True, exist_ok=True)
        base = report_base_path(output_dir)
        md_path = base.with_suffix(".md")
        md_path.write_text(markdown, encoding="utf-8")
        print(f"Wrote {md_path}")

        if args.json:
            json_path = base.with_suffix(".json")
            json_path.write_text(
                json.dumps(render_json(root, changes, args.project, excluded_hidden), ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            print(f"Wrote {json_path}")

        if not args.quiet:
            print()
            print(markdown)
    else:
        print(markdown)

    if args.fail_on_block and any(change.decision == "BLOCK" for change in changes):
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
