#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List

from skill_suite_schema import validate_suite_document

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
    # Prefer PyYAML when available.
    try:
        import yaml  # type: ignore

        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except ModuleNotFoundError:
        # Fallback without Python dependency: Ruby's stdlib YAML parser.
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
    suffix = path.suffix.lower()
    if suffix in {".yaml", ".yml"}:
        return _load_yaml(path)
    return _load_json(path)


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


def _as_list_of_str(value: object) -> List[str]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError("Expected a list")
    return [str(x) for x in value]


def _normalize_case(case: dict, index: int, source: str) -> dict:
    case_id = str(case.get("id") or "").strip()
    if not case_id:
        raise ValueError(f"{source} case #{index} missing required 'id'")

    prompt = case.get("prompt")
    if not isinstance(prompt, str) or not prompt.strip():
        raise ValueError(f"{source} case '{case_id}' missing required non-empty 'prompt'")

    expected = case.get("expected", {})
    if expected is None:
        expected = {}
    if not isinstance(expected, dict):
        raise ValueError(f"{source} case '{case_id}' field 'expected' must be an object")

    try:
        must_include = _as_list_of_str(expected.get("must_include", []))
        must_not_include = _as_list_of_str(expected.get("must_not_include", []))
    except ValueError as exc:
        raise ValueError(
            f"{source} case '{case_id}' fields expected.must_include/must_not_include must be arrays"
        ) from exc

    return {
        "id": case_id,
        "prompt": prompt,
        "expected": {
            "must_include": must_include,
            "must_not_include": must_not_include,
        },
    }


def _load_prompts(config: dict) -> List[dict]:
    if isinstance(config.get("cases"), list):
        cases = config.get("cases")
        prompts: List[dict] = []
        for i, case in enumerate(cases, start=1):
            if not isinstance(case, dict):
                raise ValueError(f"YAML case #{i} must be an object")
            prompts.append(_normalize_case(case, i, "YAML"))
        return prompts

    prompts_file = config.get("prompts_file")
    if not prompts_file:
        raise ValueError("Eval config requires 'cases' or 'prompts_file'")

    prompts_path = _resolve(str(prompts_file))
    rows = _load_jsonl(prompts_path)
    prompts = []
    for i, row in enumerate(rows, start=1):
        if not isinstance(row, dict):
            raise ValueError(f"prompts_file case #{i} must be an object")
        prompts.append(_normalize_case(row, i, f"prompts_file:{prompts_path}"))
    if not prompts:
        raise ValueError(f"prompts_file is empty: {prompts_path}")
    return prompts


def _strip_eval_suffix(file_name: str) -> str:
    for suffix in (".eval_config.json", ".eval.yaml", ".eval.yml"):
        if file_name.endswith(suffix):
            return file_name[: -len(suffix)]
    return file_name


def _is_default_eval_config(file_name: str) -> bool:
    return file_name in {"eval_config.json", "eval.yaml", "eval.yml"}


def _eval_name(config_path: Path, config: dict) -> str:
    if isinstance(config.get("eval_name"), str) and config["eval_name"].strip():
        return config["eval_name"].strip()
    if _is_default_eval_config(config_path.name):
        return "eval"
    return _strip_eval_suffix(config_path.name)


def _run_codex_case(config: dict, prompt_id: str, prompt_text: str) -> tuple[str, dict]:
    def _coerce_text(value: object) -> str:
        if isinstance(value, bytes):
            return value.decode("utf-8", errors="replace")
        if value is None:
            return ""
        return str(value)

    codex_bin = shutil.which("codex")
    if not codex_bin:
        raise RuntimeError("codex CLI not found in PATH; cannot run live evals")

    timeout_seconds = int(config.get("codex_timeout_seconds", 180))
    sandbox_mode = str(config.get("codex_sandbox", "read-only"))
    model = str(config.get("codex_model", "")).strip()
    reasoning_effort = str(config.get("codex_reasoning_effort", "")).strip()
    extra_args = config.get("codex_extra_args", [])
    if extra_args is None:
        extra_args = []
    if not isinstance(extra_args, list) or any(not isinstance(x, str) for x in extra_args):
        raise ValueError("Config field 'codex_extra_args' must be an array of strings")

    with tempfile.NamedTemporaryFile(prefix=f"skill-eval-{prompt_id}-", suffix=".txt") as out_file:
        cmd = [
            codex_bin,
            "exec",
            "--ephemeral",
            "--color",
            "never",
            "--sandbox",
            sandbox_mode,
            "--output-last-message",
            out_file.name,
        ]
        if model:
            cmd.extend(["--model", model])
        if reasoning_effort:
            cmd.extend(["-c", f'model_reasoning_effort="{reasoning_effort}"'])
        cmd.extend(extra_args)
        cmd.append(prompt_text)

        started = time.monotonic()
        timed_out = False
        error = ""
        try:
            proc = subprocess.run(
                cmd,
                cwd=str(ROOT),
                text=True,
                capture_output=True,
                timeout=timeout_seconds,
            )
            return_code = proc.returncode
            stdout = _coerce_text(proc.stdout)
            stderr = _coerce_text(proc.stderr)
        except subprocess.TimeoutExpired as exc:
            timed_out = True
            return_code = 124
            stdout = _coerce_text(exc.stdout)
            stderr = _coerce_text(exc.stderr)
            error = f"codex exec timeout after {timeout_seconds}s"

        duration_ms = int((time.monotonic() - started) * 1000)

        response_text = Path(out_file.name).read_text(encoding="utf-8").strip()
        if not response_text and not error and return_code != 0:
            stderr_preview = " ".join(stderr.strip().split())
            error = f"codex exec failed (rc={return_code})"
            if stderr_preview:
                error = f"{error}: {stderr_preview[:300]}"

        metadata = {
            "return_code": return_code,
            "timed_out": timed_out,
            "duration_ms": duration_ms,
            "error": error,
            "stdout_tail": stdout.strip()[-500:],
            "stderr_tail": stderr.strip()[-500:],
        }
        return response_text, metadata


def _required_pass_rate(config: dict) -> float:
    if "rate" in config:
        return float(config["rate"])
    return float(config.get("min_pass_rate", 1.0))


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


def grade_eval(
    config: dict,
    prompts: List[dict],
    responses: Dict[str, str],
    execution_meta: Dict[str, dict],
) -> dict:
    required_rate = _required_pass_rate(config)
    rows = []
    passed = 0

    for prompt in prompts:
        prompt_id = str(prompt["id"])
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
                "prompt": prompt.get("prompt", ""),
                "pass": ok,
                "found_response": found_response,
                "missing_required_markers": missing,
                "forbidden_markers_present": forbidden,
                "response": response_text,
                "codex_exec": execution_meta.get(prompt_id, {}),
            }
        )

    total = len(rows)
    pass_rate = (passed / total) if total else 0.0
    if total == 0:
        verdict = "skipped"
    else:
        verdict = "pass" if pass_rate >= required_rate else "fail"

    return {
        "skill": config.get("skill", "unknown"),
        "suite_class": config.get("suite_class"),
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "rate": required_rate,
        "summary": {
            "total": total,
            "passed": passed,
            "failed": total - passed,
            "pass_rate": round(pass_rate, 4),
            "verdict": verdict,
        },
        "runner": {
            "mode": "live_codex_exec",
            "codex_timeout_seconds": int(config.get("codex_timeout_seconds", 180)),
            "codex_sandbox": str(config.get("codex_sandbox", "read-only")),
            "codex_model": str(config.get("codex_model", "")).strip() or None,
            "codex_reasoning_effort": str(config.get("codex_reasoning_effort", "")).strip() or None,
        },
        "results": rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run live targeted evals and grade marker contracts.")
    parser.add_argument(
        "--config",
        required=True,
        help="Path to eval config (JSON legacy config or YAML single-file suite)",
    )
    parser.add_argument("--out", required=True, help="Path to output report JSON")
    args = parser.parse_args()

    config_path = _resolve(args.config)
    out_path = _resolve(args.out)

    try:
        config = _load_config(config_path)
        schema_errors = validate_suite_document(config_path, config)
        if schema_errors:
            parser.error("Schema validation failed: " + " | ".join(schema_errors))
        prompts = _load_prompts(config)
    except ValueError as exc:
        parser.error(str(exc))

    responses: Dict[str, str] = {}
    execution_meta: Dict[str, dict] = {}
    for prompt in prompts:
        prompt_id = str(prompt["id"])
        response_text, meta = _run_codex_case(config, prompt_id, str(prompt.get("prompt", "")))
        responses[prompt_id] = response_text
        execution_meta[prompt_id] = meta

    report = grade_eval(config, prompts, responses, execution_meta)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    summary = report["summary"]
    eval_name = _eval_name(config_path, config)
    label = f"eval:{report['skill']}/{eval_name}"
    details = f"{summary['passed']}/{summary['total']} pass  rate={summary['pass_rate']:.3f}"
    print(f"{_icon(summary['verdict'])} {label:<{LABEL_WIDTH}} {details}", flush=True)

    return 0 if summary["verdict"] != "fail" else 1


if __name__ == "__main__":
    raise SystemExit(main())
