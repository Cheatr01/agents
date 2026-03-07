#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from skill_suite_schema import load_config, schema_path, validate_suite_document

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


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a skill suite YAML against the schema.")
    parser.add_argument("--config", required=True, help="Path to suite YAML config")
    parser.add_argument("--out", required=True, help="Path to output report JSON")
    args = parser.parse_args()
    started = time.monotonic()

    config_path = _resolve(args.config)
    out_path = _resolve(args.out)

    try:
        config = load_config(config_path)
        errors = validate_suite_document(config_path, config)
    except Exception as exc:
        errors = [str(exc)]
        config = None

    verdict = "pass" if not errors else "fail"
    duration_ms = int((time.monotonic() - started) * 1000)
    report = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "config_path": str(config_path),
        "schema_path": str(schema_path()),
        "duration_ms": duration_ms,
        "summary": {
            "total": 1,
            "passed": 1 if verdict == "pass" else 0,
            "failed": 0 if verdict == "pass" else 1,
            "verdict": verdict,
            "duration_ms": duration_ms,
        },
        "results": [
            {
                "config": str(config_path),
                "skill": (config or {}).get("skill"),
                "pass": verdict == "pass",
                "errors": errors,
            }
        ],
    }

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    details = "schema ok" if verdict == "pass" else f"{len(errors)} error(s)"
    details = f"{details}  t={duration_ms}ms"
    print(f"{_icon(verdict)} {'schema-lint':<{LABEL_WIDTH}} {details}", flush=True)
    return 0 if verdict == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
