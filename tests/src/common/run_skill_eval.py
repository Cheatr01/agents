#!/usr/bin/env python3
from __future__ import annotations

import argparse
import concurrent.futures
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

try:
    import tomllib  # type: ignore[attr-defined]
except ModuleNotFoundError:  # pragma: no cover
    tomllib = None  # type: ignore[assignment]

from skill_suite_schema import validate_suite_document

ROOT = Path(__file__).resolve().parents[3]
GLOBAL_EVAL_CONFIG_PATH = ROOT / "eval-config.toml"
DEFAULT_CODEX_HOME = Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex"))).expanduser()
ISOLATED_CODEX_HOME_BASE_ENV = "EVAL_CODEX_HOME_BASE_DIR"
LABEL_WIDTH = 34
PARALLEL_START_STAGGER_MS = 500
RUNNER_DEFAULTS = {
    "max_concurrency": 3,
    "codex_timeout_seconds": 180,
    "codex_sandbox": "read-only",
    "codex_model": "",
    "codex_reasoning_effort": "",
    "codex_extra_args": [],
    "codex_isolation": False,
    "codex_home_base_dir": "",
}


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


def _load_toml(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    if tomllib is not None:
        data = tomllib.loads(text)
        if not isinstance(data, dict):
            raise ValueError(f"TOML config must be a mapping/object: {path}")
        return data

    data: dict[str, Any] = {}
    current: dict[str, Any] = data

    def parse_value(raw: str) -> Any:
        value = raw.strip()
        if value.startswith('"') and value.endswith('"'):
            return value[1:-1]
        if value in {"true", "false"}:
            return value == "true"
        if value.startswith("[") and value.endswith("]"):
            inner = value[1:-1].strip()
            if not inner:
                return []
            items = []
            for part in inner.split(","):
                item = part.strip()
                if not item.startswith('"') or not item.endswith('"'):
                    raise ValueError(f"Unsupported TOML array item in {path}: {item}")
                items.append(item[1:-1])
            return items
        if re.fullmatch(r"-?\d+", value):
            return int(value)
        raise ValueError(f"Unsupported TOML value in {path}: {value}")

    for line_no, raw_line in enumerate(text.splitlines(), start=1):
        line = raw_line.split("#", 1)[0].strip()
        if not line:
            continue
        if line.startswith("[") and line.endswith("]"):
            section_name = line[1:-1].strip()
            if not section_name:
                raise ValueError(f"Empty TOML section name at {path}:{line_no}")
            current = data
            for part in section_name.split("."):
                part = part.strip()
                if not part:
                    raise ValueError(f"Invalid TOML section name at {path}:{line_no}")
                current = current.setdefault(part, {})
                if not isinstance(current, dict):
                    raise ValueError(f"TOML section collision at {path}:{line_no}")
            continue
        if "=" not in line:
            raise ValueError(f"Invalid TOML assignment at {path}:{line_no}")
        key, raw_value = line.split("=", 1)
        key = key.strip()
        if not key:
            raise ValueError(f"Empty TOML key at {path}:{line_no}")
        current[key] = parse_value(raw_value)

    return data


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
    if suffix == ".toml":
        return _load_toml(path)
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


def _load_global_eval_config() -> dict:
    if not GLOBAL_EVAL_CONFIG_PATH.exists():
        return {}
    data = _load_toml(GLOBAL_EVAL_CONFIG_PATH)
    if not isinstance(data.get("defaults", {}), dict):
        raise ValueError(f"[defaults] must be a table in {GLOBAL_EVAL_CONFIG_PATH}")
    eval_type_cfg = data.get("eval_type", {})
    if eval_type_cfg and not isinstance(eval_type_cfg, dict):
        raise ValueError(f"[eval_type] must be a table in {GLOBAL_EVAL_CONFIG_PATH}")
    return data


def _effective_runtime_config(config: dict) -> dict:
    effective: dict[str, Any] = dict(RUNNER_DEFAULTS)

    global_cfg = _load_global_eval_config()
    defaults_cfg = global_cfg.get("defaults", {})
    if isinstance(defaults_cfg, dict):
        for key in RUNNER_DEFAULTS:
            if key in defaults_cfg:
                effective[key] = defaults_cfg[key]

    eval_type = str(config.get("eval_type", "")).strip()
    eval_type_cfg = global_cfg.get("eval_type", {})
    if eval_type and isinstance(eval_type_cfg, dict):
        per_type = eval_type_cfg.get(eval_type, {})
        if isinstance(per_type, dict):
            for key in RUNNER_DEFAULTS:
                if key in per_type:
                    effective[key] = per_type[key]

    for key in RUNNER_DEFAULTS:
        if key in config:
            effective[key] = config[key]

    env_home_base = os.getenv(ISOLATED_CODEX_HOME_BASE_ENV, "").strip()
    if env_home_base:
        effective["codex_home_base_dir"] = env_home_base

    return effective


def _default_isolated_codex_home_base_dir() -> Path:
    return Path(tempfile.gettempdir()) / "codex-evals"


def _resolve_isolated_codex_home_base_dir(runtime_config: dict) -> Path:
    raw = str(runtime_config.get("codex_home_base_dir", "")).strip()
    if raw:
        return Path(raw).expanduser().resolve()
    return _default_isolated_codex_home_base_dir().resolve()


def _validate_runtime_config(runtime_config: dict) -> None:
    if not isinstance(runtime_config.get("max_concurrency"), int):
        raise ValueError("Effective runtime config field 'max_concurrency' must be an integer")
    if int(runtime_config["max_concurrency"]) < 1:
        raise ValueError("Effective runtime config field 'max_concurrency' must be >= 1")
    if not isinstance(runtime_config.get("codex_timeout_seconds"), int):
        raise ValueError("Effective runtime config field 'codex_timeout_seconds' must be an integer")
    if int(runtime_config["codex_timeout_seconds"]) < 1:
        raise ValueError("Effective runtime config field 'codex_timeout_seconds' must be >= 1")
    if runtime_config.get("codex_sandbox") not in {"read-only", "workspace-write", "danger-full-access"}:
        raise ValueError("Effective runtime config field 'codex_sandbox' is invalid")
    if not isinstance(runtime_config.get("codex_isolation"), bool):
        raise ValueError("Effective runtime config field 'codex_isolation' must be a boolean")
    if not isinstance(runtime_config.get("codex_extra_args"), list) or any(
        not isinstance(x, str) for x in runtime_config.get("codex_extra_args", [])
    ):
        raise ValueError("Effective runtime config field 'codex_extra_args' must be an array of strings")


def _sanitize_name(value: str) -> str:
    safe = re.sub(r"[^A-Za-z0-9._-]+", "-", value.strip())
    return safe.strip("-") or "eval"


def _symlink_path(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.symlink_to(src, target_is_directory=src.is_dir())


def _copy_path(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def _seed_isolated_codex_home(config: dict, isolated_home: Path) -> None:
    # Keep only the minimum auth/state artifacts needed to run Codex, not the full config with MCP servers.
    for name in ("auth.json", ".codex-global-state.json", "version.json", "models_cache.json"):
        src = DEFAULT_CODEX_HOME / name
        if src.exists():
            _copy_path(src, isolated_home / name)

    (isolated_home / "skills").mkdir(parents=True, exist_ok=True)
    (isolated_home / "config.toml").write_text(
        "# Generated by tests/src/common/run_skill_eval.py\n",
        encoding="utf-8",
    )

    if str(config.get("eval_type", "")).strip() != "skill":
        return

    skill_name = str(config.get("skill", "")).strip()
    skill_path = _resolve(str(config.get("skill_path", "")).strip())
    skill_dir = skill_path.parent
    if not skill_name:
        raise ValueError("Skill eval isolation requires non-empty 'skill'")
    if not skill_path.exists():
        raise ValueError(f"Skill eval isolation requires existing skill_path: {skill_path}")
    _symlink_path(skill_dir, isolated_home / "skills" / skill_name)


def _suite_codex_env(config_path: Path, config: dict, runtime_config: dict) -> tuple[dict[str, str], dict]:
    env = os.environ.copy()
    suite_meta = {
        "codex_isolation": bool(runtime_config.get("codex_isolation", False)),
        "codex_home_base_dir": str(_resolve_isolated_codex_home_base_dir(runtime_config)),
        "codex_home": None,
        "max_concurrency": int(runtime_config.get("max_concurrency", 1)),
    }

    if not suite_meta["codex_isolation"]:
        return env, suite_meta

    base_dir = _resolve_isolated_codex_home_base_dir(runtime_config)
    base_dir.mkdir(parents=True, exist_ok=True)
    tempdir = tempfile.TemporaryDirectory(
        prefix=f"codex-eval-{_sanitize_name(str(config.get('skill', 'skill')))}-{_sanitize_name(_eval_name(config_path, config))}-",
        dir=str(base_dir),
    )
    suite_root = Path(tempdir.name)
    template_home = suite_root / "template-home"
    case_homes_dir = suite_root / "case-homes"
    _seed_isolated_codex_home(config, template_home)
    case_homes_dir.mkdir(parents=True, exist_ok=True)
    env["CODEX_HOME"] = str(template_home)
    suite_meta["codex_home"] = str(template_home)
    suite_meta["_template_home"] = str(template_home)
    suite_meta["_case_homes_dir"] = str(case_homes_dir)
    suite_meta["_tempdir"] = tempdir
    return env, suite_meta


def _case_codex_env(suite_runtime_meta: dict, prompt_id: str) -> tuple[dict[str, str], Any | None]:
    env = os.environ.copy()
    if not suite_runtime_meta.get("codex_isolation"):
        codex_home = suite_runtime_meta.get("codex_home")
        if codex_home:
            env["CODEX_HOME"] = str(codex_home)
        return env, None

    case_homes_dir = Path(str(suite_runtime_meta["_case_homes_dir"]))
    template_home = Path(str(suite_runtime_meta["_template_home"]))
    tempdir = tempfile.TemporaryDirectory(
        prefix=f"case-{_sanitize_name(prompt_id)}-",
        dir=str(case_homes_dir),
    )
    case_home = Path(tempdir.name)

    for name in ("auth.json", ".codex-global-state.json", "version.json", "models_cache.json", "config.toml"):
        src = template_home / name
        if src.exists():
            _copy_path(src, case_home / name)

    skills_src = template_home / "skills"
    if skills_src.exists():
        _symlink_path(skills_src, case_home / "skills")

    env["CODEX_HOME"] = str(case_home)
    return env, tempdir


def _run_codex_case(
    runtime_config: dict,
    codex_env: dict[str, str],
    prompt_id: str,
    prompt_text: str,
) -> tuple[str, dict]:
    def _coerce_text(value: object) -> str:
        if isinstance(value, bytes):
            return value.decode("utf-8", errors="replace")
        if value is None:
            return ""
        return str(value)

    codex_bin = shutil.which("codex")
    if not codex_bin:
        raise RuntimeError("codex CLI not found in PATH; cannot run live evals")

    timeout_seconds = int(runtime_config.get("codex_timeout_seconds", 180))
    sandbox_mode = str(runtime_config.get("codex_sandbox", "read-only"))
    model = str(runtime_config.get("codex_model", "")).strip()
    reasoning_effort = str(runtime_config.get("codex_reasoning_effort", "")).strip()
    extra_args = runtime_config.get("codex_extra_args", [])
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
                env=codex_env,
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


def _is_retryable_codex_error(meta: dict) -> bool:
    haystack = " ".join(
        [
            str(meta.get("error") or ""),
            str(meta.get("stderr_tail") or ""),
            str(meta.get("stdout_tail") or ""),
        ]
    ).lower()
    needles = (
        "stream disconnected",
        "failed to refresh available models",
        "error sending request for url",
        "reconnecting...",
    )
    return any(needle in haystack for needle in needles)


def _run_prompt_case(
    prompt: dict,
    runtime_config: dict,
    suite_runtime_meta: dict,
    *,
    start_delay_ms: int = 0,
) -> tuple[str, str, dict]:
    prompt_id = str(prompt["id"])
    prompt_text = str(prompt.get("prompt", ""))
    if start_delay_ms > 0:
        time.sleep(start_delay_ms / 1000)
    case_env, case_tempdir = _case_codex_env(suite_runtime_meta, prompt_id)
    try:
        response_text, meta = _run_codex_case(runtime_config, case_env, prompt_id, prompt_text)
    finally:
        if case_tempdir is not None:
            case_tempdir.cleanup()
    return prompt_id, response_text, meta


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
    runtime_config: dict,
    suite_runtime_meta: dict,
    total_duration_ms: int,
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
        "eval_type": config.get("eval_type", "unknown"),
        "skill": config.get("skill", "unknown"),
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "duration_ms": total_duration_ms,
        "rate": required_rate,
        "summary": {
            "total": total,
            "passed": passed,
            "failed": total - passed,
            "pass_rate": round(pass_rate, 4),
            "verdict": verdict,
            "duration_ms": total_duration_ms,
        },
        "runner": {
            "mode": "live_codex_exec",
            "global_config_path": str(GLOBAL_EVAL_CONFIG_PATH) if GLOBAL_EVAL_CONFIG_PATH.exists() else None,
            "max_concurrency": int(runtime_config.get("max_concurrency", 1)),
            "effective_concurrency": int(suite_runtime_meta.get("effective_concurrency", 1)),
            "serial_retry_count": int(suite_runtime_meta.get("serial_retry_count", 0)),
            "codex_timeout_seconds": int(runtime_config.get("codex_timeout_seconds", 180)),
            "codex_sandbox": str(runtime_config.get("codex_sandbox", "read-only")),
            "codex_model": str(runtime_config.get("codex_model", "")).strip() or None,
            "codex_reasoning_effort": str(runtime_config.get("codex_reasoning_effort", "")).strip() or None,
            "codex_extra_args": list(runtime_config.get("codex_extra_args", [])),
            "codex_isolation": bool(runtime_config.get("codex_isolation", False)),
            "codex_home_base_dir": suite_runtime_meta.get("codex_home_base_dir"),
            "codex_home": suite_runtime_meta.get("codex_home"),
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
    started = time.monotonic()

    config_path = _resolve(args.config)
    out_path = _resolve(args.out)

    try:
        config = _load_config(config_path)
        schema_errors = validate_suite_document(config_path, config)
        if schema_errors:
            parser.error("Schema validation failed: " + " | ".join(schema_errors))
        runtime_config = _effective_runtime_config(config)
        _validate_runtime_config(runtime_config)
        prompts = _load_prompts(config)
    except ValueError as exc:
        parser.error(str(exc))

    responses: Dict[str, str] = {}
    execution_meta: Dict[str, dict] = {}
    codex_env, suite_runtime_meta = _suite_codex_env(config_path, config, runtime_config)
    tempdir = suite_runtime_meta.pop("_tempdir", None)
    try:
        if suite_runtime_meta.get("codex_isolation"):
            # Shared template only; each case gets its own CODEX_HOME clone to avoid concurrent state writes.
            suite_runtime_meta["codex_home"] = suite_runtime_meta.get("_template_home", suite_runtime_meta.get("codex_home"))
        else:
            suite_runtime_meta["codex_home"] = codex_env.get("CODEX_HOME")

        max_workers = min(max(1, int(runtime_config.get("max_concurrency", 1))), max(1, len(prompts)))
        suite_runtime_meta["effective_concurrency"] = max_workers
        suite_runtime_meta["serial_retry_count"] = 0
        if max_workers == 1:
            for prompt in prompts:
                prompt_id, response_text, meta = _run_prompt_case(prompt, runtime_config, suite_runtime_meta)
                responses[prompt_id] = response_text
                execution_meta[prompt_id] = meta
        else:
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = [
                    executor.submit(
                        _run_prompt_case,
                        prompt,
                        runtime_config,
                        suite_runtime_meta,
                        start_delay_ms=index * PARALLEL_START_STAGGER_MS,
                    )
                    for index, prompt in enumerate(prompts)
                ]
                for future in concurrent.futures.as_completed(futures):
                    prompt_id, response_text, meta = future.result()
                    responses[prompt_id] = response_text
                    execution_meta[prompt_id] = meta

            retry_prompts = []
            for prompt in prompts:
                prompt_id = str(prompt["id"])
                meta = execution_meta.get(prompt_id, {})
                if responses.get(prompt_id, "").strip():
                    continue
                if _is_retryable_codex_error(meta):
                    retry_prompts.append(prompt)

            if retry_prompts:
                suite_runtime_meta["serial_retry_count"] = len(retry_prompts)
                for prompt in retry_prompts:
                    prompt_id, response_text, meta = _run_prompt_case(prompt, runtime_config, suite_runtime_meta)
                    previous_meta = execution_meta.get(prompt_id, {})
                    if previous_meta:
                        meta["retry"] = {
                            "mode": "serial_after_parallel_failure",
                            "previous_duration_ms": previous_meta.get("duration_ms"),
                            "previous_error": previous_meta.get("error"),
                        }
                    responses[prompt_id] = response_text
                    execution_meta[prompt_id] = meta
    finally:
        if tempdir is not None:
            tempdir.cleanup()

    total_duration_ms = int((time.monotonic() - started) * 1000)
    report = grade_eval(
        config,
        runtime_config,
        suite_runtime_meta,
        total_duration_ms,
        prompts,
        responses,
        execution_meta,
    )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    summary = report["summary"]
    eval_name = _eval_name(config_path, config)
    label = f"eval:{report['skill']}/{eval_name}"
    details = (
        f"{summary['passed']}/{summary['total']} pass  "
        f"rate={summary['pass_rate']:.3f}  t={summary['duration_ms']}ms"
    )
    print(f"{_icon(summary['verdict'])} {label:<{LABEL_WIDTH}} {details}", flush=True)

    return 0 if summary["verdict"] != "fail" else 1


if __name__ == "__main__":
    raise SystemExit(main())
