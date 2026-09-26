"""Verification never dispatches formal execution; RUN is an explicit separate command."""
import argparse
import os
from pathlib import Path
import subprocess
import sys
from .artifacts import environment, implementation_fingerprint, new_directory, read_json, write_json
from .performance import Performance


def verify(output, root):
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
        write_json(args.output, Performance(**read_json(args.performance)).as_dict())
        return 0
    if args.command == "freeze-baseline":
        from .baseline import freeze_baseline
        freeze_baseline(root, args.baseline, args.baseline_id, args.baseline_version,
                        args.verification, read_json(args.performance), args.device,
                        args.predecessor, args.reason)
        return 0
    if args.command == "run-one":
        from .runner import run_one
        status = run_one(args.master_seed, args.output, root, args.baseline, args.attempt_id,
                         args.retry_of, args.retry_reason)
        print(status)
        return 0 if status["execution_status"] == "VALID" else 1
    if args.command == "aggregate":
        from .aggregation import aggregate_baseline
        print(aggregate_baseline(args.baseline, args.output)["classification"])
        return 0
    from .runner import reanalyze
    print(reanalyze(args.run, args.output, root)["evaluation_flags"])
    return 0
