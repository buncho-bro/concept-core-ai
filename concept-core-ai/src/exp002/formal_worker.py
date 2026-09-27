"""Fresh formal worker: guard process-start environment before scientific imports."""
import argparse
import json
import os
from pathlib import Path
import sys


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
    provenance = validate_process_start(args.baseline, _PROCESS_START_ENVIRONMENT, tuple(sys.modules))
    if args.validate_only:
        print(json.dumps(provenance, sort_keys=True))
        return 0
    if args.master_seed is None or args.attempt_id is None or args.output is None:
        parser.error("formal execution requires seed, attempt ID and output")
    # Every scientific import and the non-importable formal execution body are
    # intentionally below the stdlib-only process-start guard.
    from . import runner
    from .baseline import registered_attempt, validate_runtime
    from .config import FORMAL_SEEDS, SOURCE_COMMIT, configuration, seeds_for
    from .performance import Performance
    root = Path(__file__).resolve().parents[2]
    if args.master_seed not in FORMAL_SEEDS:
        raise ValueError("Formal execution requires an approved master seed")
    manifest = validate_runtime(root, args.baseline)
    registered_manifest, registration = registered_attempt(
        args.baseline, args.master_seed, args.attempt_id, args.output)
    if registered_manifest["manifest_hash"] != manifest["manifest_hash"]:
        raise ValueError("Registered attempt manifest changed before worker execution")
    performance = Performance(**manifest["frozen_performance"])
    applied_torch = performance.apply_formal(provenance)
    os.environ.setdefault("CUBLAS_WORKSPACE_CONFIG", ":4096:8")
    runner.configure_precision()
    config = {
        **configuration(),
        "run_id": Path(args.output).name,
        "formal": True,
        "master_seed": args.master_seed,
        "seeds": seeds_for(args.master_seed),
        "git_commit": manifest["execution_commit"],
        "canonical_source_commit": SOURCE_COMMIT,
        "environment": manifest["required_environment"],
        "performance": performance.as_dict(),
        "device": manifest["device"],
        "device_class": manifest["device_class"],
        "implementation": manifest["implementation"],
        "baseline_id": manifest["baseline_id"],
        "baseline_version": manifest["baseline_version"],
        "baseline_manifest_hash": manifest["manifest_hash"],
        "verification_receipt_sha256": manifest["verification"]["sha256"],
        "attempt_id": args.attempt_id,
        "attempt_kind": registration["attempt_kind"],
        "parent_canonical_attempt_id": registration["parent_canonical_attempt_id"],
        "performance_runtime": {
            "process_start": provenance,
            "applied_torch": applied_torch,
            "dataloader": {
                "num_workers": performance.num_workers,
                "persistent_workers": performance.persistent_workers,
            },
        },
    }

    def execute_guarded_attempt():
        """Local-only formal body; it cannot be imported or called around the guard."""
        output = runner.new_directory(args.output)
        status = {"execution_status": "INVALID", "evaluation_flags": [], "complete": False,
                  "reason": "An interrupted attempt remains INVALID"}
        runner.write_json(output / "configuration.json", config)
        runner.write_json(output / "verification.json", manifest["verification"]["receipt"])
        runner.write_json(output / "status.json", status)
        try:
            rows = runner.assign_splits(
                runner.generate_metadata(config["seeds"]["generation_seed"]),
                config["seeds"]["split_seed"],
            )
            runner.write_metadata(output / "metadata.csv", rows)
            indices = runner.split_indices(rows)
            runner.save_npz(output / "split.npz", **indices)
            images = runner.generate_images(rows, output / "images.npy")
            datasets = {
                split: runner.SplitDataset(images, rows, indices[split], split)
                for split in runner.ACTIVE_SPLITS
            }
            model = runner.Autoencoder(config["seeds"]["model_seed"])
            config["parameter_count"] = sum(parameter.numel() for parameter in model.parameters())
            runner.write_json(output / "configuration.json", config, replace=True)
            runner.train(
                model, datasets["train"], datasets["validation"],
                config["seeds"]["loader_seed"], output, config["device"], performance,
            )
            runner.export_states(
                model, images, datasets, indices, rows, config["seeds"]["loader_seed"],
                output, config["device"], performance,
            )
            evaluation = runner.evaluate_saved(output, output / "evaluation")
            status.update(execution_status="VALID", evaluation_flags=evaluation["evaluation_flags"],
                          complete=True, reason=None)
        except runner.ExperimentalFailure as exc:
            status.update(execution_status="EXPERIMENTAL_FAILURE", complete=True, reason=str(exc))
            runner.write_json(output / "failure.json", {
                "type": type(exc).__name__, "message": str(exc),
                "traceback": runner.traceback.format_exc(),
            })
        except BaseException as exc:
            status.update(execution_status="INVALID", complete=False, reason=str(exc))
            runner.write_json(output / "failure.json", {
                "type": type(exc).__name__, "message": str(exc),
                "traceback": runner.traceback.format_exc(),
            })
            raise
        finally:
            runner.write_json(output / "status.json", status, replace=True)
            runner.write_json(output / "report.json", {
                "OBSERVATIONS": "Execution and measurements only; classification is experiment-level.",
                "METRICS": ["training.csv", "reconstruction_metrics.json", "evaluation/summary.json"],
                "WARNINGS": status,
                "ARTIFACTS": sorted(runner.inventory(output)),
                "formal": True,
            })
            runner.write_json(output / "integrity.json", runner.inventory(output))
        return status

    status = execute_guarded_attempt()
    print(status)
    return 0 if status["execution_status"] == "VALID" else 1


if __name__ == "__main__":
    raise SystemExit(main())
