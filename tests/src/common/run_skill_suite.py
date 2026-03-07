#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import List

ROOT = Path(__file__).resolve().parents[3]
SKILLS_TESTS_DIR = ROOT / "tests" / "src" / "skills"
STEP_LABEL_WIDTH = 28


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


def _fmt_step_line(status: str, label: str, detail: str = "") -> str:
    if detail:
        return f"  {_icon(status)} {label:<{STEP_LABEL_WIDTH}} {detail}"
    return f"  {_icon(status)} {label:<{STEP_LABEL_WIDTH}}"


def _print_subprocess_failure(prefix: str, proc: subprocess.CompletedProcess[str]) -> None:
    stdout = (proc.stdout or "").strip()
    stderr = (proc.stderr or "").strip()
    if stdout:
        print(f"  {_icon('info')} {prefix} stdout:", flush=True)
        for line in stdout.splitlines():
            print(f"      {line}", flush=True)
    if stderr:
        print(f"  {_icon('info')} {prefix} stderr:", flush=True)
        for line in stderr.splitlines():
            print(f"      {line}", flush=True)


def _resolve(path_str: str) -> Path:
    p = Path(path_str)
    if p.is_absolute():
        return p
    return (ROOT / p).resolve()


def _run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=str(ROOT), text=True, capture_output=True)


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


def _discover_eval_configs(skill_dir: Path) -> List[Path]:
    candidates: List[Path] = []
    for default_name in ("eval_config.json", "eval.yaml", "eval.yml"):
        default_cfg = skill_dir / default_name
        if default_cfg.exists():
            candidates.append(default_cfg)

    for pattern in ("*.eval_config.json", "*.eval.yaml", "*.eval.yml"):
        for path in sorted(skill_dir.glob(pattern)):
            if path not in candidates:
                candidates.append(path)

    return candidates


def _strip_eval_suffix(file_name: str) -> str:
    for suffix in (".eval_config.json", ".eval.yaml", ".eval.yml"):
        if file_name.endswith(suffix):
            return file_name[: -len(suffix)]
    return file_name


def _is_default_eval_config(file_name: str) -> bool:
    return file_name in {"eval_config.json", "eval.yaml", "eval.yml"}


def _eval_output_name(config_path: Path, config: dict) -> str:
    if isinstance(config.get("eval_name"), str) and config["eval_name"].strip():
        return config["eval_name"].strip()
    if _is_default_eval_config(config_path.name):
        return "eval"
    return _strip_eval_suffix(config_path.name)


def _fallback_eval_output_name(config_path: Path) -> str:
    if _is_default_eval_config(config_path.name):
        return "eval"
    return _strip_eval_suffix(config_path.name)


def _find_embedded_gate_config(eval_configs: List[Path]) -> Path | None:
    for cfg_path in eval_configs:
        try:
            cfg = _load_config(cfg_path)
        except Exception:
            continue
        if isinstance(cfg.get("gate_requirements"), dict):
            return cfg_path
    return None


def run_skill_suite(skill_name: str, out_dir: Path) -> tuple[int, dict]:
    skill_dir = SKILLS_TESTS_DIR / skill_name
    summary = {
        "skill": skill_name,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "skill_test_dir": str(skill_dir),
        "out_dir": str(out_dir),
        "steps": [],
    }

    if not skill_dir.exists() or not skill_dir.is_dir():
        summary["summary"] = {
            "verdict": "fail",
            "reason": "missing skill test directory",
            "steps_total": 0,
            "steps_passed": 0,
            "steps_failed": 1,
            "steps_skipped": 0,
        }
        return 1, summary

    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"{_icon('info')} skill {skill_name}", flush=True)

    eval_configs = _discover_eval_configs(skill_dir)
    schema_validity: dict[Path, bool] = {}

    # Step 0: schema lint (for suite YAML configs)
    if eval_configs:
        for cfg_path in eval_configs:
            schema_name = _fallback_eval_output_name(cfg_path)
            schema_out = out_dir / f"{schema_name}.schema.json"
            cmd = [
                "python3",
                "tests/src/common/run_skill_schema_lint.py",
                "--config",
                str(cfg_path.relative_to(ROOT)),
                "--out",
                str(schema_out.relative_to(ROOT)),
            ]
            proc = _run(cmd)
            rc = proc.returncode
            schema_validity[cfg_path] = rc == 0
            schema_detail = ""
            if schema_out.exists():
                try:
                    schema_report = _load_json(schema_out)
                    schema_summary = schema_report.get("summary", {})
                    schema_detail = "schema ok" if rc == 0 else f"{schema_summary.get('failed', 0)} failure"
                except Exception:
                    schema_detail = "report parse error"
            else:
                schema_detail = "missing report"
            summary["steps"].append(
                {
                    "type": "schema_lint",
                    "name": f"schema:{schema_name}",
                    "config": str(cfg_path),
                    "output": str(schema_out),
                    "detail": schema_detail,
                    "status": "pass" if rc == 0 else "fail",
                    "exit_code": rc,
                }
            )
            print(_fmt_step_line("pass" if rc == 0 else "fail", f"schema:{schema_name}", schema_detail), flush=True)
            if rc != 0:
                _print_subprocess_failure(f"schema:{schema_name}", proc)

    # Step 1: gate lint (if per-skill gate config exists)
    embedded_gate_cfg = _find_embedded_gate_config(eval_configs)
    legacy_gate_cfg = skill_dir / "gate_requirements.json"
    gate_cfg = None
    if embedded_gate_cfg is not None and schema_validity.get(embedded_gate_cfg, False):
        gate_cfg = embedded_gate_cfg
    elif legacy_gate_cfg.exists():
        gate_cfg = legacy_gate_cfg
    if gate_cfg is not None:
        gate_out = out_dir / "gate-lint.json"
        cmd = [
            "python3",
            "tests/src/common/run_skill_gate_lint.py",
            "--requirements",
            str(gate_cfg.relative_to(ROOT)),
            "--out",
            str(gate_out.relative_to(ROOT)),
        ]
        proc = _run(cmd)
        rc = proc.returncode
        gate_detail = ""
        if gate_out.exists():
            try:
                gate_report = _load_json(gate_out)
                gate_summary = gate_report.get("summary", {})
                gate_detail = f"{gate_summary.get('passed', 0)}/{gate_summary.get('total', 0)} checks"
            except Exception:
                gate_detail = "report parse error"
        else:
            gate_detail = "missing report"
        summary["steps"].append(
            {
                "type": "gate_lint",
                "name": "gate-lint",
                "config": str(gate_cfg),
                "output": str(gate_out),
                "detail": gate_detail,
                "status": "pass" if rc == 0 else "fail",
                "exit_code": rc,
            }
        )
        print(_fmt_step_line("pass" if rc == 0 else "fail", "gate-lint", gate_detail), flush=True)
        if rc != 0:
            _print_subprocess_failure("gate-lint", proc)
    else:
        summary["steps"].append(
            {
                "type": "gate_lint",
                "name": "gate-lint",
                "status": "skipped",
                "reason": "missing valid embedded or legacy gate requirements",
            }
        )
        print(_fmt_step_line("skipped", "gate-lint", "no valid embedded/legacy gate config"), flush=True)

    # Step 2+: evals (0..n configs)
    if eval_configs:
        for cfg_path in eval_configs:
            eval_name = _fallback_eval_output_name(cfg_path)
            if not schema_validity.get(cfg_path, False):
                summary["steps"].append(
                    {
                        "type": "eval",
                        "name": eval_name,
                        "config": str(cfg_path),
                        "status": "skipped",
                        "reason": "schema validation failed",
                    }
                )
                print(_fmt_step_line("skipped", f"eval:{eval_name}", "schema validation failed"), flush=True)
                continue
            cfg = _load_config(cfg_path)
            eval_name = _eval_output_name(cfg_path, cfg)
            out_path = out_dir / f"{eval_name}.eval.json"
            cmd = [
                "python3",
                "tests/src/common/run_skill_eval.py",
                "--config",
                str(cfg_path.relative_to(ROOT)),
                "--out",
                str(out_path.relative_to(ROOT)),
            ]
            proc = _run(cmd)
            rc = proc.returncode
            eval_detail = ""
            eval_status = "pass" if rc == 0 else "fail"
            if out_path.exists():
                try:
                    eval_report = _load_json(out_path)
                    eval_summary = eval_report.get("summary", {})
                    eval_status = str(eval_summary.get("verdict", eval_status))
                    eval_detail = (
                        f"{eval_summary.get('passed', 0)}/{eval_summary.get('total', 0)} pass  "
                        f"rate={float(eval_summary.get('pass_rate', 0.0)):.3f}"
                    )
                except Exception:
                    eval_detail = "report parse error"
            else:
                eval_detail = "missing report"
            summary["steps"].append(
                {
                    "type": "eval",
                    "name": eval_name,
                    "config": str(cfg_path),
                    "output": str(out_path),
                    "detail": eval_detail,
                    "status": eval_status,
                    "exit_code": rc,
                }
            )
            print(_fmt_step_line(eval_status, f"eval:{eval_name}", eval_detail), flush=True)
            if rc != 0:
                _print_subprocess_failure(f"eval:{eval_name}", proc)
    else:
        summary["steps"].append(
            {
                "type": "eval",
                "name": "evals",
                "status": "skipped",
                "reason": "no eval config (json/yaml)",
            }
        )
        print(_fmt_step_line("skipped", "evals", "no eval config"), flush=True)

    steps_total = len(summary["steps"])
    steps_passed = sum(1 for s in summary["steps"] if s["status"] == "pass")
    steps_failed = sum(1 for s in summary["steps"] if s["status"] == "fail")
    steps_skipped = sum(1 for s in summary["steps"] if s["status"] == "skipped")

    if steps_failed:
        verdict = "fail"
        rc = 1
    elif steps_passed == 0:
        verdict = "skipped"
        rc = 0
    else:
        verdict = "pass"
        rc = 0

    summary["summary"] = {
        "verdict": verdict,
        "steps_total": steps_total,
        "steps_passed": steps_passed,
        "steps_failed": steps_failed,
        "steps_skipped": steps_skipped,
    }

    return rc, summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Run isolated test flow for one skill.")
    parser.add_argument("--skill", required=True, help="Skill name under tests/src/skills")
    parser.add_argument(
        "--out-dir",
        help="Output directory for this skill (default: tests/results/skills/<skill>)",
    )
    parser.add_argument(
        "--summary-out",
        help="Optional explicit path for suite summary JSON (default: <out-dir>/suite-summary.json)",
    )
    args = parser.parse_args()

    skill_name = args.skill.strip()
    if not skill_name:
        parser.error("--skill must not be empty")

    out_dir = _resolve(args.out_dir) if args.out_dir else (ROOT / "tests" / "results" / "skills" / skill_name)
    summary_out = _resolve(args.summary_out) if args.summary_out else (out_dir / "suite-summary.json")

    rc, summary = run_skill_suite(skill_name, out_dir)

    summary_out.parent.mkdir(parents=True, exist_ok=True)
    summary_out.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    s = summary["summary"]
    suite_detail = f"pass={s['steps_passed']}  fail={s['steps_failed']}  skipped={s['steps_skipped']}"
    print(_fmt_step_line(s["verdict"], "suite", suite_detail), flush=True)
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
