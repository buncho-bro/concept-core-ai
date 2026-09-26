# TEST_AUDIT

完全非formal suite: merge commit `7084b32` を独立 worktree で実行。**231 passed、0 failed、0 skipped、0 errors、14 warnings、113.99 秒**。warnings は Matplotlib/pyparsing の deprecation warnings。formal run は 0。

| 領域 | 質 | 所見 |
| --- | --- | --- |
| arbitrary-attempt cherry picking | A/C | `test_arbitrary_attempt_cherry_picking_cannot_change_formal_classification` は alternate record で旧 `aggregate_records` が変わることを示したうえで baseline registry の canonical result を確認。PASS。 |
| first registration / retry | B/C | duplicate canonical を拒否し、retry parent/reason、INVALID/EXPERIMENTAL_FAILURE canonical + VALID retry の判定を確認。PASS。 |
| manifest / performance mutation | B | performance knobs の manifest self-hash 改竄と canonical run record mismatch を確認。seed/commit/fingerprint/receipt/environment/device/id/version/predecessor の個別 mutation test は限定的だが、同じ self-hash verifier が全 field に適用される。PASS。 |
| successor baseline | C | predecessor hash/reason/v2 empty slots/v1 preserve は確認。Human authorization が任意文字列なので E: insufficient（REV-002-03）。 |
| environment variables | E | `OMP_NUM_THREADS`/`MKL_NUM_THREADS` が Python 起動前の native runtime と一致することを確認するテストがない（REV-002-02）。 |
| CLI restriction / aggregation | B | arbitrary five paths と per-run performance 引数を argparse が拒否。PASS。 |
| pre-RUN registration | C | mocked `_execute_attempt` 時点で canonical registration 済みを検査。PASS。 |
| scientific mathematics regression | B | 既存 aggregation / loss / probe / distance / bootstrap tests が全通過。PR #6 から §40 Step 1–7 のロジック変更なし。PASS。 |

旧 exploit reproduction: caller-selected alternate attempt は `aggregate_records`（internal pure helper）では依然異なる分類を作れるが、supported formal CLI/`aggregate_baseline` では registry canonical artifact 以外を入力にできず、old REV-002-01 exploit は再現不能だった。
