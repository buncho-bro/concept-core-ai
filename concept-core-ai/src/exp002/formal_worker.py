"""Fresh formal worker: guard process-start environment before scientific imports."""
import argparse
import json
import os
from pathlib import Path
import sys


_MODULES_AT_ENTRY = tuple(sys.modules)
_PROCESS_START_ENVIRONMENT = {name: os.environ.get(name) for name in ("OMP_NUM_THREADS", "MKL_NUM_THREADS")}


def main(argv=None):
    parser = argparse.ArgumentParser(description="Internal Exp002 formal worker")
    parser.add_argument("--baseline", required=True)
    parser.add_argument("--master-seed", type=int)
    parser.add_argument("--attempt-id")
    parser.add_argument("--output")
    parser.add_argument("--validate-only", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    from .process_start import validate_process_start
    provenance = validate_process_start(args.baseline, _PROCESS_START_ENVIRONMENT, _MODULES_AT_ENTRY)
    if args.validate_only:
        print(json.dumps(provenance, sort_keys=True))
        return 0
    if args.master_seed is None or args.attempt_id is None or args.output is None:
        parser.error("formal execution requires seed, attempt ID and output")
    # This import is intentionally after the stdlib-only process-start guard.
    from .runner import execute_registered_attempt
    root = Path(__file__).resolve().parents[2]
    status = execute_registered_attempt(args.master_seed, args.output, root, args.baseline,
                                        args.attempt_id, provenance)
    print(status)
    return 0 if status["execution_status"] == "VALID" else 1


if __name__ == "__main__":
    raise SystemExit(main())
