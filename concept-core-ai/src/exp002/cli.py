"""Verification never dispatches formal execution; RUN is an explicit separate command."""
import argparse
import os
from pathlib import Path
import subprocess
import sys
from .artifacts import environment, implementation_fingerprint, new_directory, read_json, write_json


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
    r = commands.add_parser("run-one", help="Separate RUN stage: one formal attempt")
    r.add_argument("--mode", choices=["RUN"], required=True)
    r.add_argument("--master-seed", type=int, choices=range(1001, 1006), required=True)
    r.add_argument("--output", required=True)
    r.add_argument("--verification", required=True)
    r.add_argument("--performance", required=True, help="Frozen, preselected Performance JSON")
    r.add_argument("--device", default="cpu")
    a = commands.add_parser("aggregate")
    a.add_argument("runs", nargs="+")
    a.add_argument("--output", required=True)
    re = commands.add_parser("reanalyze")
    re.add_argument("run")
    re.add_argument("--output", required=True)
    args = parser.parse_args(argv)
    root = Path(__file__).resolve().parents[2]
    if args.command == "verify":
        return verify(args.output, root)
    if args.command == "run-one":
        from .runner import run_one
        status = run_one(args.master_seed, args.output, root, args.verification, read_json(args.performance), args.device)
        print(status)
        return 0 if status["execution_status"] == "VALID" else 1
    if args.command == "aggregate":
        from .aggregation import aggregate_paths
        print(aggregate_paths(args.runs, args.output)["classification"])
        return 0
    from .runner import reanalyze
    print(reanalyze(args.run, args.output, root)["evaluation_flags"])
    return 0
