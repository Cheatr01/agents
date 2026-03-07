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
from typing import List

ROOT = Path(__file__).resolve().parents[3]
LABEL_WIDTH = 34


def _use_color() -> bool:
    return sys.stdout.isatty() and os.getenv("NO_COLOR") is None


def _paint(text: str, color_code: str) -> str:
    if not _use_color():
        return text
    return f"\033[{color_code}m{text}\033[0m"


def _icon(verdict: str) -> str:
    return {
        "pass": _paint("✓", "32"),
        "fail": _paint("✗", "31"),
        "skipped": _paint("•", "33"),
    }.get(verdict, "·")


def _resolve(path_str: str) -> Path:
    p = Path(path_str)
    if p.is_absolute():
        return p
    return (ROOT / p).resolve()


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_yaml(path: Path) -> dict:
    try:
        import yaml  # type: ignore

        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except ModuleNotFoundError:
        proc = subprocess.run(
            [
                "ruby",
                "-rjson",
                "-ryaml",
                "-e",
                "data = YAML.safe_load(File.read(ARGV[0]), aliases: true); puts JSON.generate(data)",
                str(path),
            ],
            text=True,
            capture_output=True,
        )
        if proc.returncode != 0:
            raise ValueError(f"Unable to parse YAML config {path}: {proc.stderr.strip()}") from None
        data = json.loads(proc.stdout)

    if not isinstance(data, dict):
        raise ValueError(f"YAML config must be a mapping/object: {path}")
    return data


def _load_config(path: Path) -> dict:
    if path.suffix.lower() in {".yaml", ".yml"}:
        return _load_yaml(path)
    return _load_json(path)


def _normalize_required_snippets(raw: object, path: Path) -> list[str]:
    if raw is None:
        return []
    if not isinstance(raw, list) or any(not isinstance(item, str) for item in raw):
        raise ValueError(f"Invalid required_snippets list in {path}")
    return list(raw)


def _load_requirements_from_suite(path: Path, data: dict) -> list[dict]:
    gate = data.get("gate_requirements")
    if not isinstance(gate, dict):
        raise ValueError(f"Missing or invalid gate_requirements in {path}")

    name = str(data.get("skill") or "").strip()
    if not name:
        raise ValueError(f"Missing skill in {path}")

    skill_path = str(data.get("skill_path") or "").strip()
    if not skill_path:
        raise ValueError(f"Missing skill_path in {path}")

    item = {
        "name": name,
        "skill_path": skill_path,
        "required_snippets": _normalize_required_snippets(gate.get("required_snippets"), path),
        "_config_path": str(path),
    }
    return [item]


def _load_requirements_from_file(path: Path) -> list[dict]:
    data = _load_config(path)
    if isinstance(data, dict) and "gate_requirements" in data:
        return _load_requirements_from_suite(path, data)
    if isinstance(data, dict) and "skills" in data:
        skills = data.get("skills", [])
        if not isinstance(skills, list):
            raise ValueError(f"Invalid skills list in {path}")
        return [dict(item) for item in skills]
    if isinstance(data, dict) and "name" in data and "required_snippets" in data:
        item = dict(data)
        item["_config_path"] = str(path)
        return [item]
    raise ValueError(f"Unsupported requirements format in {path}")


def _discover_requirements(discover_dir: Path) -> list[dict]:
    rows: list[dict] = []
    for path in sorted(discover_dir.rglob("gate_requirements.json")):
        rows.extend(_load_requirements_from_file(path))
    return rows


def lint_items(requirement_items: list[dict]) -> dict:
    rows: List[dict] = []
    passed = 0

    for item in requirement_items:
        name = item["name"]
        required_snippets = list(item.get("required_snippets", []))
        skill_path = str(item.get("skill_path") or "").strip()
        skill_file = _resolve(skill_path) if skill_path else (ROOT / "skills" / name / "SKILL.md")
        config_path = item.get("_config_path")

        if not skill_file.exists():
            rows.append(
                {
                    "skill": name,
                    "skill_path": str(skill_file),
                    "config_path": config_path,
                    "pass": False,
                    "missing_file": True,
                    "missing_snippets": required_snippets,
                }
            )
            continue

        text = skill_file.read_text(encoding="utf-8")
        missing = [snippet for snippet in required_snippets if snippet not in text]
        ok = len(missing) == 0
        if ok:
            passed += 1

        rows.append(
            {
                "skill": name,
                "skill_path": str(skill_file),
                "config_path": config_path,
                "pass": ok,
                "missing_file": False,
                "missing_snippets": missing,
            }
        )

    total = len(rows)
    summary = {
        "total": total,
        "passed": passed,
        "failed": total - passed,
        "verdict": "pass" if total > 0 and passed == total else "fail",
    }

    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "summary": summary,
        "results": rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Lint required gate snippets in skill docs.")
    parser.add_argument("--requirements", help="Path to requirements JSON (single file or legacy aggregate)")
    parser.add_argument(
        "--discover-dir",
        help="Directory to recursively discover legacy per-skill gate_requirements.json files",
    )
    parser.add_argument("--out", required=True, help="Path to output report JSON")
    args = parser.parse_args()
    started = time.monotonic()

    if bool(args.requirements) == bool(args.discover_dir):
        parser.error("Provide exactly one of --requirements or --discover-dir")

    if args.requirements:
        requirement_items = _load_requirements_from_file(_resolve(args.requirements))
    else:
        requirement_items = _discover_requirements(_resolve(args.discover_dir))

    report = lint_items(requirement_items)
    duration_ms = int((time.monotonic() - started) * 1000)
    report["duration_ms"] = duration_ms
    report["summary"]["duration_ms"] = duration_ms

    out_path = _resolve(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    s = report["summary"]
    label = "gate-lint"
    details = f"{s['passed']}/{s['total']} checks  t={duration_ms}ms"
    print(f"{_icon(s['verdict'])} {label:<{LABEL_WIDTH}} {details}", flush=True)
    return 0 if s["verdict"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
