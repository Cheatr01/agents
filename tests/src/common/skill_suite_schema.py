from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
SCHEMA_PATH = ROOT / "tests" / "src" / "common" / "skill-suite.schema.yaml"

_TOP_LEVEL_KEYS = {
    "eval_type",
    "skill",
    "skill_path",
    "gate_requirements",
    "eval_name",
    "grader",
    "rate",
    "max_concurrency",
    "codex_timeout_seconds",
    "codex_isolation",
    "codex_home_base_dir",
    "codex_sandbox",
    "codex_model",
    "codex_reasoning_effort",
    "codex_extra_args",
    "cases",
}
_CASE_KEYS = {"id", "prompt", "expected"}
_EXPECTED_KEYS = {"must_include", "must_not_include"}
_GATE_KEYS = {"required_snippets"}
_EVAL_TYPE_VALUES = {"skill"}
_SANDBOX_VALUES = {"read-only", "workspace-write", "danger-full-access"}
_REASONING_VALUES = {"none", "low", "medium", "high", "xhigh"}


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


def load_config(path: Path) -> dict:
    if path.suffix.lower() in {".yaml", ".yml"}:
        return _load_yaml(path)
    return _load_json(path)


def schema_path() -> Path:
    return SCHEMA_PATH


def is_yaml_suite_config(path: Path) -> bool:
    return path.suffix.lower() in {".yaml", ".yml"}


def _json_path(parts: list[str]) -> str:
    if not parts:
        return "$"
    out = "$"
    for part in parts:
        if part.startswith("["):
            out += part
        else:
            out += f".{part}"
    return out


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _is_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _validate_string(value: Any, path: list[str], errors: list[str], *, allow_empty: bool = False) -> None:
    if not isinstance(value, str):
        errors.append(f"{_json_path(path)} must be a string")
        return
    if not allow_empty and not value.strip():
        errors.append(f"{_json_path(path)} must not be empty")


def _validate_string_list(value: Any, path: list[str], errors: list[str]) -> None:
    if not isinstance(value, list):
        errors.append(f"{_json_path(path)} must be an array of strings")
        return
    for idx, item in enumerate(value):
        if not isinstance(item, str):
            errors.append(f"{_json_path(path + [f'[{idx}]'])} must be a string")


def _validate_expected(value: Any, path: list[str], errors: list[str]) -> None:
    if not isinstance(value, dict):
        errors.append(f"{_json_path(path)} must be an object")
        return
    unknown = sorted(set(value.keys()) - _EXPECTED_KEYS)
    for key in unknown:
        errors.append(f"{_json_path(path + [key])} is not allowed")
    for key in ("must_include", "must_not_include"):
        if key in value:
            _validate_string_list(value[key], path + [key], errors)


def _validate_case(value: Any, index: int, errors: list[str]) -> None:
    path = ["cases", f"[{index}]"]
    if not isinstance(value, dict):
        errors.append(f"{_json_path(path)} must be an object")
        return

    unknown = sorted(set(value.keys()) - _CASE_KEYS)
    for key in unknown:
        errors.append(f"{_json_path(path + [key])} is not allowed")

    for key in ("id", "prompt", "expected"):
        if key not in value:
            errors.append(f"{_json_path(path)} missing required property '{key}'")

    if "id" in value:
        _validate_string(value["id"], path + ["id"], errors)
    if "prompt" in value:
        _validate_string(value["prompt"], path + ["prompt"], errors)
    if "expected" in value:
        _validate_expected(value["expected"], path + ["expected"], errors)


def _validate_gate_requirements(value: Any, errors: list[str]) -> None:
    path = ["gate_requirements"]
    if not isinstance(value, dict):
        errors.append(f"{_json_path(path)} must be an object")
        return
    unknown = sorted(set(value.keys()) - _GATE_KEYS)
    for key in unknown:
        errors.append(f"{_json_path(path + [key])} is not allowed")
    if "required_snippets" not in value:
        errors.append(f"{_json_path(path)} missing required property 'required_snippets'")
        return
    _validate_string_list(value["required_snippets"], path + ["required_snippets"], errors)


def _manual_validate(data: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["$ must be an object"]

    unknown = sorted(set(data.keys()) - _TOP_LEVEL_KEYS)
    for key in unknown:
        errors.append(f"{_json_path([key])} is not allowed")

    for key in ("eval_type", "skill", "skill_path", "grader", "rate", "cases"):
        if key not in data:
            errors.append(f"$ missing required property '{key}'")

    if "eval_type" in data:
        _validate_string(data["eval_type"], ["eval_type"], errors)
        if isinstance(data["eval_type"], str) and data["eval_type"] not in _EVAL_TYPE_VALUES:
            errors.append("$.eval_type must be one of ['skill']")
    if "skill" in data:
        _validate_string(data["skill"], ["skill"], errors)
    if "skill_path" in data:
        _validate_string(data["skill_path"], ["skill_path"], errors)
        if isinstance(data["skill_path"], str) and not data["skill_path"].endswith("SKILL.md"):
            errors.append("$.skill_path must point to SKILL.md")
    if "gate_requirements" in data:
        _validate_gate_requirements(data["gate_requirements"], errors)
    if "eval_name" in data:
        _validate_string(data["eval_name"], ["eval_name"], errors)
    if "grader" in data:
        _validate_string(data["grader"], ["grader"], errors)
        if data["grader"] != "markers":
            errors.append("$.grader must be one of ['markers']")
    if "rate" in data:
        if not _is_number(data["rate"]):
            errors.append("$.rate must be a number")
        elif not (0 <= float(data["rate"]) <= 1):
            errors.append("$.rate must be between 0 and 1")
    if "max_concurrency" in data:
        if not _is_int(data["max_concurrency"]):
            errors.append("$.max_concurrency must be an integer")
        elif int(data["max_concurrency"]) < 1:
            errors.append("$.max_concurrency must be >= 1")
    if "codex_timeout_seconds" in data:
        if not _is_int(data["codex_timeout_seconds"]):
            errors.append("$.codex_timeout_seconds must be an integer")
        elif int(data["codex_timeout_seconds"]) < 1:
            errors.append("$.codex_timeout_seconds must be >= 1")
    if "codex_isolation" in data and not isinstance(data["codex_isolation"], bool):
        errors.append("$.codex_isolation must be a boolean")
    if "codex_home_base_dir" in data:
        _validate_string(data["codex_home_base_dir"], ["codex_home_base_dir"], errors)
    if "codex_sandbox" in data:
        _validate_string(data["codex_sandbox"], ["codex_sandbox"], errors)
        if isinstance(data["codex_sandbox"], str) and data["codex_sandbox"] not in _SANDBOX_VALUES:
            errors.append(
                "$.codex_sandbox must be one of ['read-only', 'workspace-write', 'danger-full-access']"
            )
    if "codex_model" in data:
        if not isinstance(data["codex_model"], str):
            errors.append("$.codex_model must be a string")
    if "codex_reasoning_effort" in data:
        _validate_string(data["codex_reasoning_effort"], ["codex_reasoning_effort"], errors)
        if (
            isinstance(data["codex_reasoning_effort"], str)
            and data["codex_reasoning_effort"] not in _REASONING_VALUES
        ):
            errors.append(
                "$.codex_reasoning_effort must be one of ['none', 'low', 'medium', 'high', 'xhigh']"
            )
    if "codex_extra_args" in data:
        _validate_string_list(data["codex_extra_args"], ["codex_extra_args"], errors)
    if "cases" in data:
        if not isinstance(data["cases"], list):
            errors.append("$.cases must be an array")
        else:
            for idx, case in enumerate(data["cases"]):
                _validate_case(case, idx, errors)

    return errors


def _format_jsonschema_error(error: Any) -> str:
    parts: list[str] = []
    for piece in error.absolute_path:
        if isinstance(piece, int):
            parts.append(f"[{piece}]")
        else:
            parts.append(str(piece))
    return f"{_json_path(parts)}: {error.message}"


def validate_suite_document(config_path: Path, data: dict | None = None) -> list[str]:
    if not is_yaml_suite_config(config_path):
        return []

    if data is None:
        data = load_config(config_path)

    _ = load_config(SCHEMA_PATH)

    try:
        import jsonschema  # type: ignore

        schema = load_config(SCHEMA_PATH)
        validator = jsonschema.Draft202012Validator(schema)
        errors = sorted(
            validator.iter_errors(data),
            key=lambda err: (_json_path([str(p) if not isinstance(p, int) else f"[{p}]" for p in err.absolute_path]), err.message),
        )
        return [_format_jsonschema_error(error) for error in errors]
    except ModuleNotFoundError:
        return _manual_validate(data)
