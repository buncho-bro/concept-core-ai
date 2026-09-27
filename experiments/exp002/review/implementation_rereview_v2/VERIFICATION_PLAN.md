# Required verification after the next FIX

1. Invoke the official `run-one` CLI in a clean process and assert that the worker observes the manifest OMP/MKL values before NumPy, PyTorch, SciPy, or scikit-learn import.
2. Assert that an OMP/MKL mismatch terminates before any scientific import or artifact creation.
3. Assert that every supported public execution entry point rejects direct execution unless it is reached through the guarded fresh worker; include the formerly reachable `execute_registered_attempt` path.
4. Assert attempt registration exists before child launch and that a child-start failure preserves the registered attempt status.
5. Test a valid, committed authorization record and each invalid variant: untracked, modified, wrong predecessor, wrong successor, wrong version, wrong Decision ID, bad integrity hash, and mismatched Git blob/source commit.
6. Run the authorization tests on Windows with an explicit decoding policy, then run the full suite. Required result: no test failures.
7. Freeze a v2 successor with a valid authorization and confirm run and aggregate revalidate the same record. Confirm v1 behavior remains unchanged.
8. Confirm runtime provenance recorded in an attempt agrees exactly with the frozen manifest and that aggregate invalidates disagreement.
9. Confirm no formal experiment is run while performing these tests, and preserve all failure records.
