# NEW_BLOCKERS

## REV-002-01 — 正式 attempt の選択を固定できない

- **Location:** `src/exp002/cli.py:53-55`、`src/exp002/aggregation.py:54-69,160-162`、`src/exp002/runner.py:176-189`。仕様 §40 Step 1、§47、§50。
- **Type:** `STATUS_SEMANTICS` / `ARTIFACT_INTEGRITY`。
- **Expected:** 事前に特定された正規5 seed の formal attempt 集合だけで判定し、失敗・不利な attempt を黙って別 attempt に差し替えない。全 attempt は保存し、最終集合の由来を再構成できる。
- **Observed:** `run-one` は同じ seed/commit/性能設定で別の出力先へ何度でも作成可能。`aggregate` は呼び出し側が渡した任意の5 path だけを読み、別 path に存在する同 seed の attempt を発見・拒否・記録しない。`aggregate_records` は渡された5件が整合すれば SUCCESS 等へ進む。独立した非formalメモリ fixture で、同 commit/設定の seed 1件だけを別 attempt に差し替えると `INCONCLUSIVE` と `SUCCESS` の両方が得られることを確認した。実装ガイドの「never chooses favorable reruns」という主張は、呼び出し側による選択を防ぐ保証ではない。
- **Why it matters:** 結果確認後に好ましい run を選べ、正式5 run の科学的判定が変わる。
- **Required next step:** **FIX**。正式 baseline の attempt 登録・選定を監査可能に固定し、余分な／重複 attempt や差し替えがある場合に黙って三値判定へ進まないようにする。失敗 attempt の保持と、やり直し時の provenance を検証する非formalテストを追加する。既存仕様だけでは再試行の選定規則が一意でないと判断された場合、その規則に限り Human の **DECISION** を求める。レビュー側は規則を決定しない。

## REV-002-02 — 性能設定の RUN 前凍結が証明されない

- **Location:** `src/exp002/cli.py:36,49-52`、`src/exp002/runner.py:176-189`、`src/exp002/artifacts.py:15-29`。仕様 §46–47、§50。
- **Type:** `DETERMINISM` / `ARTIFACT_INTEGRITY`。
- **Expected:** wall-clock のみで選んだ性能設定を最初の formal RUN 前に固定し、全5 seed に同一設定を使う。formal 結果を見て設定を選び直せないことを追跡できる。
- **Observed:** CLI は任意の JSON を各 `run-one` 呼び出し時に受け付ける。`Performance` は値の妥当性を検査し、run 設定には記録するが、`require_verification` の receipt に凍結済み設定・時点は含まれず、runner は事前凍結記録との一致を確認しない。Aggregator は選ばれた5 run 間の同一性のみ検査するため、formal 結果を見た後に新たな5件を同じ別設定で揃える経路を防がない。
- **Why it matters:** formal 結果に基づく事後的な性能設定選択を、機械的監査では排除できない。実行順序・環境設定が数値結果と判定に影響し得る。
- **Required next step:** **FIX**。最初の formal RUN より前に固定した性能設定の証跡を作り、runner と aggregation がそれへの一致を検証できるようにする。設定変更・事後作成を拒む非formalテストを追加する。凍結手段のファイル形式や CLI は実装詳細であり、研究条件は変えない。
