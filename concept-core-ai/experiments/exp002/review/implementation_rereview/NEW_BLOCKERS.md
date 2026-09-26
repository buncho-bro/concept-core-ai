# NEW_BLOCKERS

## REV-002-03 — 後継 baseline の Human authorization を識別・検証できない

- **Location:** `src/exp002/baseline.py:48-91` (`freeze_baseline`)、`src/exp002/cli.py:36-69`、spec §50A、Decision HD-002-01。
- **Type:** `PROVENANCE` / `ATTEMPT_SELECTION`。
- **Expected:** canonical attempt の置換を目的とする successor baseline は Human が決めた場合だけ作成され、承認の追跡可能な識別子が manifest に保存・検証される。単なる自己申告の reason は承認証跡ではない。
- **Observed:** `freeze-baseline --predecessor <v1> --reason <任意の非空文字列>` は、Human approval reference を要求・検証せず v2 を作れる。実装テストも `reason="Human-authorized restart"` を任意文字列として渡すだけで通る。v2 は空 canonical slots を持つため、v1 の不利な canonical attempt を使わず、新しい5 attempt を正規集合として扱える。
- **Reproduction:** non-formal fixture で v1 に canonical attempt を登録後、任意の `--reason` 相当文字列で v2 を freeze できる。CLI/API は Human Decision の ID、承認 commit/hash、署名済み record 等を参照しない。
- **Why it matters:** HD-002-01 の「If Human decides」境界を supported workflow が保証せず、baseline version 作成を用いた結果依存の canonical-set 再作成が監査上区別できない。
- **Required next step:** **FIX**。successor manifest に Human authorization を指す不変で検証可能な provenance（例: 承認済み Decision の ID と immutable commit/hash）を必須化し、v2 が v1 attempt 登録後に authorization なしで作れないことを非formalテストで確認する。承認 artifact の正規形式が未決なら、その形式だけ Human の **DECISION** を求める。
