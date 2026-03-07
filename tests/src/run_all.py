#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

ROOT = Path(__file__).resolve().parents[2]
SKILLS_TESTS_DIR = ROOT / "tests" / "src" / "skills"
RESULTS_DIR = ROOT / "tests" / "results"
REPO_LABEL_WIDTH = 28


def _use_color() -> bool:
    return sys.stdout.isatty() and os.getenv("NO_COLOR") is None


def _paint(text: str, color_code: str) -> str:
    if not _use_color():
        return text
    return f"\033[{color_code}m{text}\033[0m"


def _icon(status: str) -> str:
    return {
        "pass": _paint("✓", "32"),
        "fail": _paint("✗", "31"),
        "skipped": _paint("•", "33"),
        "info": _paint("›", "36"),
    }.get(status, "·")


def _run(cmd: list[str]) -> int:
    return subprocess.call(cmd, cwd=str(ROOT))


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _discover_skills() -> list[str]:
    if not SKILLS_TESTS_DIR.exists():
        return []
    return sorted([p.name for p in SKILLS_TESTS_DIR.iterdir() if p.is_dir()])


def _parse_skills_arg(values: Optional[List[str]]) -> list[str]:
    if not values:
        return []
    skills: list[str] = []
    for raw in values:
        for part in raw.split(","):
            name = part.strip()
            if name:
                skills.append(name)
    # preserve order, remove duplicates
    seen = set()
    uniq = []
    for s in skills:
        if s not in seen:
            uniq.append(s)
            seen.add(s)
    return uniq


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Run isolated skill test suites for all skills in tests/src/skills or for selected skills."
        )
    )
    parser.add_argument(
        "--skills",
        nargs="*",
        help="Optional list (or comma-separated list) of skill names to test",
    )
    args = parser.parse_args()
    started = time.monotonic()

    discovered = _discover_skills()
    if not discovered:
        print("No skill test directories found under tests/src/skills")
        return 1

    selected = _parse_skills_arg(args.skills)
    if selected:
        unknown = [s for s in selected if s not in discovered]
        if unknown:
            print(f"Unknown skill test directories: {', '.join(unknown)}")
            return 2
        skills_to_run = selected
    else:
        skills_to_run = discovered

    mode_label = "repo-suite:selected" if selected else "repo-suite:all"
    print(
        f"{_icon('info')} {mode_label:<{REPO_LABEL_WIDTH}} skills={len(skills_to_run)}",
        flush=True,
    )

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    (RESULTS_DIR / "skills").mkdir(parents=True, exist_ok=True)

    repo_summary = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "mode": "selected" if selected else "all",
        "skills_requested": selected,
        "skills_discovered": discovered,
        "skills_run": [],
    }

    exit_code = 0
    for skill in skills_to_run:
        out_dir = RESULTS_DIR / "skills" / skill
        suite_summary_path = out_dir / "suite-summary.json"
        cmd = [
            "python3",
            "tests/src/common/run_skill_suite.py",
            "--skill",
            skill,
            "--out-dir",
            str(out_dir.relative_to(ROOT)),
            "--summary-out",
            str(suite_summary_path.relative_to(ROOT)),
        ]
        skill_started = time.monotonic()
        rc = _run(cmd)
        skill_duration_ms = int((time.monotonic() - skill_started) * 1000)
        if rc != 0:
            exit_code = 1

        if suite_summary_path.exists():
            suite_summary = _load_json(suite_summary_path)
            repo_summary["skills_run"].append(
                {
                    "skill": skill,
                    "verdict": suite_summary.get("summary", {}).get("verdict", "unknown"),
                    "duration_ms": suite_summary.get("summary", {}).get("duration_ms", skill_duration_ms),
                    "summary_file": str(suite_summary_path),
                }
            )
        else:
            repo_summary["skills_run"].append(
                {
                    "skill": skill,
                    "verdict": "fail",
                    "duration_ms": skill_duration_ms,
                    "summary_file": str(suite_summary_path),
                    "reason": "missing suite summary",
                }
            )
            exit_code = 1

    total = len(repo_summary["skills_run"])
    passed = sum(1 for r in repo_summary["skills_run"] if r["verdict"] == "pass")
    failed = sum(1 for r in repo_summary["skills_run"] if r["verdict"] == "fail")
    skipped = sum(1 for r in repo_summary["skills_run"] if r["verdict"] == "skipped")
    repo_summary["summary"] = {
        "total_skills": total,
        "passed": passed,
        "failed": failed,
        "skipped": skipped,
        "verdict": "pass" if failed == 0 else "fail",
        "duration_ms": int((time.monotonic() - started) * 1000),
    }

    repo_summary_path = RESULTS_DIR / "repo-suite-summary.json"
    repo_summary_path.write_text(json.dumps(repo_summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    s = repo_summary["summary"]
    print(
        f"{_icon(s['verdict'])} {'repo-suite':<{REPO_LABEL_WIDTH}} "
        f"total={s['total_skills']}  pass={s['passed']}  fail={s['failed']}  "
        f"skipped={s['skipped']}  t={s['duration_ms']}ms"
    )
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
