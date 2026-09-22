# NEW_BLOCKERS

## NB-01 — 5 runを束ねるExperiment-level評価単位が未定義

Section 18は成果物を1 run単位で保存し、各`report.md`へSUCCESS / INCONCLUSIVE / NO_EVIDENCEを記録するよう要求している。しかし最終判定には5 runが必要である。

IMPLEMENT前にHumanによる決定が必要な事項:

- どの5つの`run_id`を正式baseline集合とするか
- その集合を実行前にどこへ固定するか
- 集約結果を保存するExperiment-level成果物
- run失敗時に同一seedを再実行するか、失敗値として扱うか
- 5件未満の有効runで判定を禁止するか
