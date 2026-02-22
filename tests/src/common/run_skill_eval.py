#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple

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


def _load_jsonl(path: Path) -> List[dict]:
    text = path.read_text(encoding="utf-8")

    # Fast path: classic JSONL (one object per line).
    rows: List[dict] = []
    line_mode_ok = True
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            line_mode_ok = False
            break
    if line_mode_ok:
        return rows

    # Fallback: parse a stream of JSON objects separated by whitespace/newlines.
    rows = []
    decoder = json.JSONDecoder()
    idx = 0
    n = len(text)
    while idx < n:
        while idx < n and text[idx].isspace():
            idx += 1
        if idx >= n:
            break
        obj, end = decoder.raw_decode(text, idx)
        rows.append(obj)
        idx = end
    return rows


def _extract_response_text(row: dict) -> str:
    for key in ("response", "output", "answer", "text"):
        value = row.get(key)
        if isinstance(value, str):
            return value
    return ""


def _find_missing(text_lc: str, markers: List[str]) -> List[str]:
    missing: List[str] = []
    for marker in markers:
        if marker.lower() not in text_lc:
            missing.append(marker)
    return missing


def _find_forbidden(text_lc: str, markers: List[str]) -> List[str]:
    present: List[str] = []
    for marker in markers:
        if marker.lower() in text_lc:
            present.append(marker)
    return present


def grade_eval(config: dict, prompts: List[dict], responses: Dict[str, str]) -> dict:
    min_pass_rate = float(config.get("min_pass_rate", 1.0))
    rows = []
    passed = 0

    for prompt in prompts:
        prompt_id = str(prompt["id"])
        category = prompt.get("category", "unspecified")
        expected = prompt.get("expected", {})
        must_include = list(expected.get("must_include", []))
        must_not_include = list(expected.get("must_not_include", []))

        response_text = responses.get(prompt_id, "")
        response_lc = response_text.lower()

        missing = _find_missing(response_lc, must_include)
        forbidden = _find_forbidden(response_lc, must_not_include)
        found_response = bool(response_text.strip())

        ok = found_response and not missing and not forbidden
        if ok:
            passed += 1

        rows.append(
            {
                "id": prompt_id,
                "category": category,
                "pass": ok,
                "found_response": found_response,
                "missing_required_markers": missing,
                "forbidden_markers_present": forbidden,
            }
        )

    total = len(rows)
    pass_rate = (passed / total) if total else 0.0
    verdict = "pass" if total > 0 and pass_rate >= min_pass_rate else "fail"

    return {
        "skill": config.get("skill", "unknown"),
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "min_pass_rate": min_pass_rate,
        "summary": {
            "total": total,
            "passed": passed,
            "failed": total - passed,
            "pass_rate": round(pass_rate, 4),
            "verdict": verdict,
        },
        "results": rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Grade targeted skill eval responses.")
    parser.add_argument("--config", required=True, help="Path to eval config JSON")
    parser.add_argument("--responses", help="Path to responses JSONL (optional if config provides responses_file)")
    parser.add_argument("--out", required=True, help="Path to output report JSON")
    args = parser.parse_args()

    config_path = _resolve(args.config)
    out_path = _resolve(args.out)

    config = _load_json(config_path)
    responses_path_str = args.responses or config.get("responses_file")
    if not responses_path_str:
        parser.error("Responses file must be provided via --responses or config.responses_file")
    responses_path = _resolve(responses_path_str)

    raw_responses = _load_jsonl(responses_path)
    responses = {str(r.get("id")): _extract_response_text(r) for r in raw_responses}

    prompts_file = config.get("prompts_file")
    if not prompts_file:
        parser.error("eval config requires prompts_file")
    prompts_path = _resolve(prompts_file)
    prompts = _load_jsonl(prompts_path)
    report = grade_eval(config, prompts, responses)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    summary = report["summary"]
    eval_name = str(config.get("eval_name") or "eval")
    label = f"eval:{report['skill']}/{eval_name}"
    details = f"{summary['passed']}/{summary['total']} pass  rate={summary['pass_rate']:.3f}"
    print(f"{_icon(summary['verdict'])} {label:<{LABEL_WIDTH}} {details}", flush=True)

    return 0 if summary["verdict"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
