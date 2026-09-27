"""Verification never dispatches formal execution; RUN is an explicit separate command."""
import argparse
import os
from pathlib import Path
import subprocess
import sys


def verify(output, root):
    from .artifacts import environment, implementation_fingerprint, new_directory, write_json
    output = new_directory(output)
    before, runtime = implementation_fingerprint(root), environment()
    with (output / "pytest.txt").open("x", encoding="utf-8") as stream:
        result = subprocess.run([sys.executable, "-m", "pytest", str(root / "tests"), "-q",
            f"--junitxml={output.resolve() / 'junit.xml'}"], cwd=root, stdout=stream, stderr=subprocess.STDOUT,
            check=False, env={**os.environ, "PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8"})
    unchanged = before == implementation_fingerprint(root)
    code = result.returncode if unchanged else 1
    write_json(output / "verification.json", {"experiment_id": "exp002", "mode": "IMPLEMENT_VERIFY",
        "formal_runs_executed": 0, "exit_code": code, "implementation": before, "environment": runtime,
        "implementation_unchanged_during_verification": unchanged})
    print((output / "pytest.txt").read_text(encoding="utf-8"))
    return code


def launch_formal(args, root):
    """Register once, then launch a fresh worker with frozen process-start settings."""
    from .process_start import load_process_start_requirements
    child_environment = os.environ.copy()
    process_start = load_process_start_requirements(args.baseline)
    child_environment.update(process_start)
    # Parent scientific imports after child env construction cannot initialize the fresh child.
    from .baseline import register_attempt, validate_runtime
    manifest = validate_runtime(root, args.baseline)
    registration = register_attempt(args.baseline, args.master_seed, args.attempt_id, args.output,
                                    args.retry_of, args.retry_reason)
    command = [sys.executable, "-m", "exp002.formal_worker", "--baseline", args.baseline,
               "--master-seed", str(args.master_seed), "--attempt-id", args.attempt_id,
               "--output", args.output]

    def record_start_failure(reason, returncode=None):
        from .artifacts import inventory, new_directory, write_json
        output = new_directory(args.output)
        write_json(output / "status.json", {
            "execution_status": "INVALID", "evaluation_flags": [], "complete": False,
            "reason": reason,
        })
        write_json(output / "worker_start_failure.json", {
            "type": "WORKER_START_FAILURE",
            "reason": reason,
            "returncode": returncode,
            "registration": registration,
            "baseline_manifest_hash": manifest["manifest_hash"],
            "process_start": {"required": process_start, "launcher_environment": process_start},
            "command_module": "exp002.formal_worker",
        })
        write_json(output / "integrity.json", inventory(output))

    try:
        result = subprocess.run(command, cwd=root, env=child_environment, check=False)
    except OSError as exc:
        record_start_failure(f"Formal worker could not start: {exc}")
        return 1
    if result.returncode and not Path(args.output).exists():
        record_start_failure(f"Formal worker exited before creating attempt artifacts: {result.returncode}",
                             result.returncode)
    return result.returncode


def main(argv=None):
    parser = argparse.ArgumentParser(description="Experiment 002 approved specification")
    commands = parser.add_subparsers(dest="command", required=True)
    v = commands.add_parser("verify", help="Synthetic fixtures only; no formal run")
    v.add_argument("--output", required=True)
    p = commands.add_parser("prepare-performance", help="Normalize a non-formal wall-clock benchmark selection")
    p.add_argument("--performance", required=True)
    p.add_argument("--output", required=True)
    f = commands.add_parser("freeze-baseline", help="Freeze verified provenance before the first formal run")
    f.add_argument("--baseline", required=True)
    f.add_argument("--baseline-id", required=True)
    f.add_argument("--baseline-version", required=True)
    f.add_argument("--verification", required=True)
    f.add_argument("--performance", required=True)
    f.add_argument("--device", default="cpu")
    f.add_argument("--predecessor")
    f.add_argument("--reason")
    f.add_argument("--authorization")
    r = commands.add_parser("run-one", help="Separate RUN stage: one formal attempt")
    r.add_argument("--mode", choices=["RUN"], required=True)
    r.add_argument("--master-seed", type=int, choices=range(1001, 1006), required=True)
    r.add_argument("--baseline", required=True)
    r.add_argument("--attempt-id", required=True)
    r.add_argument("--output", required=True)
    r.add_argument("--retry-of")
    r.add_argument("--retry-reason")
    a = commands.add_parser("aggregate", help="Resolve the formal five only from a frozen baseline")
    a.add_argument("--baseline", required=True)
    a.add_argument("--output", required=True)
    re = commands.add_parser("reanalyze")
    re.add_argument("run")
    re.add_argument("--output", required=True)
    args = parser.parse_args(argv)
    root = Path(__file__).resolve().parents[2]
    if args.command == "verify":
        return verify(args.output, root)
    if args.command == "prepare-performance":
        from .artifacts import read_json, write_json
        from .performance import Performance
        write_json(args.output, Performance(**read_json(args.performance)).as_dict())
        return 0
    if args.command == "freeze-baseline":
        from .artifacts import read_json
        from .baseline import freeze_baseline
        freeze_baseline(root, args.baseline, args.baseline_id, args.baseline_version,
                        args.verification, read_json(args.performance), args.device,
                        args.predecessor, args.reason, args.authorization)
        return 0
    if args.command == "run-one":
        return launch_formal(args, root)
    if args.command == "aggregate":
        from .aggregation import aggregate_baseline
        print(aggregate_baseline(args.baseline, args.output)["classification"])
        return 0
    from .runner import reanalyze
    print(reanalyze(args.run, args.output, root)["evaluation_flags"])
    return 0
