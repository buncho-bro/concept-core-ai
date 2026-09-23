"""Verification, single formal execution, reanalysis and aggregation are separate."""
import argparse
import os
from pathlib import Path
import subprocess
import sys
from .artifacts import environment, implementation_fingerprint, new_directory, write_json


def verify(output, root):
    output = new_directory(output)
    log = output / "pytest.txt"
    before = implementation_fingerprint(root)
    runtime = environment()
    with log.open("x", encoding="utf-8") as stream:
        result = subprocess.run([sys.executable, "-m", "pytest", str(root / "tests"), "-q",
                                 f"--junitxml={output.resolve() / 'junit.xml'}"], cwd=root,
                                stdout=stream, stderr=subprocess.STDOUT, check=False,
                                env={**os.environ, "PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8"})
    log_text = log.read_text(encoding="utf-8")
    unchanged = before == implementation_fingerprint(root)
    exit_code = result.returncode if unchanged else 1
    receipt = {"mode": "IMPLEMENT_VERIFY", "formal_runs_executed": 0, "exit_code": exit_code,
               "implementation": before, "implementation_unchanged_during_verification": unchanged,
               "environment": runtime}
    write_json(output / "verification.json", receipt)
    print(log_text)
    return exit_code


def main(argv=None):
    parser = argparse.ArgumentParser(description="Experiment 001 fixed approved baseline")
    commands = parser.add_subparsers(dest="command", required=True)
    v = commands.add_parser("verify", help="Run fixtures only, never a formal experiment")
    v.add_argument("--output", required=True)
    r = commands.add_parser("run-one", help="RUN mode: one formal 50-epoch experiment")
    r.add_argument("--master-seed", type=int, choices=range(1001, 1006), required=True)
    r.add_argument("--output", required=True)
    r.add_argument("--verification", required=True)
    r.add_argument("--device", default="cpu")
    a = commands.add_parser("aggregate", help="Aggregate an explicitly selected formal run set")
    a.add_argument("runs", nargs="+")
    a.add_argument("--output", required=True)
    re = commands.add_parser("reanalyze", help="Recompute evaluation from saved artifacts into a new directory")
    re.add_argument("run")
    re.add_argument("--output", required=True)
    args = parser.parse_args(argv)
    root = Path(__file__).resolve().parents[2]
    if args.command == "verify":
        return verify(args.output, root)
    if args.command == "run-one":
        from .runner import run_one
        status = run_one(args.master_seed, args.output, root, args.verification, args.device)
        print(status)
        return 0 if status["execution_status"] == "VALID" else 1
    if args.command == "aggregate":
        from .aggregation import aggregate_paths
        print(aggregate_paths(args.runs, args.output)["classification"])
        return 0
    from .runner import reanalyze
    print(reanalyze(args.run, args.output)["evaluation_flags"])
    return 0
