# TRACEABILITY

| 要求 | 実装根拠 | 判定 |
| --- | --- | --- |
| immutable baseline manifest | `baseline.py:freeze_baseline/load_manifest` が schema、id/version、5 seed、commit、fingerprint、receipt hash/payload、environment/device、performance、predecessor、self-hash を保存・検証 | PASS（後継承認は REV-002-03） |
| pre-RUN registration / first wins | `runner.py:run_one` は runtime 検証後、`register_attempt` を `_execute_attempt` より先に呼ぶ。canonical JSON は exclusive create | PASS |
| retry non-replacement | `register_attempt` は canonical parent と reason を必須化。`aggregate_baseline` は canonical のみ分類し retry は audit | PASS |
| canonical artifact / manifest binding | `aggregation.py:_validate_canonical_record` が output、commit、fingerprint、receipt hash、environment、device、performance、baseline fields を照合 | PASS |
| old arbitrary paths API removal | `cli.py:aggregate` は `--baseline` だけ。`aggregate_paths` は production formal entry point から削除 | PASS |
| frozen performance input | `runner.py:run_one` は manifest の `frozen_performance` だけを `Performance` へ渡し CLI performance override はなし | PARTIAL：OMP/MKL 起動時環境の検証不足（REV-002-02） |
| successor baseline governance | predecessor id/hash と reason は保存され、v1 は変更されず v2 slots は空 | FAIL：Human authorization を検証しない（REV-002-03） |
| §40 Step 1–7 | `aggregate_records` の数式・順序は PR #6 と同一。PR #7 は canonical record の入力選定を追加 | PASS |

Crash window: canonical registration は output 作成より先であり、直後・output作成後・training中・完了前の crash は registration を残す。次 attempt は retry としてのみ登録でき、canonical output 不在／不完全は Step 1 `NOT_EVALUATED` になる。PASS。
