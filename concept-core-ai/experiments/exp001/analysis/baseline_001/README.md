# Experiment 001 — baseline 001 post-run analysis

**Experiment-level classification: INCONCLUSIVE**（確定済み、変更なし）。本ディレクトリは正式5 runの事後的な科学的解釈であり、再分類、閾値調整、新規実験ではない。

## 出典と固定範囲

- 仕様: [spec.md](https://github.com/buncho-bro/concept-core-ai/blob/e9791b236e2c2618ed77e031e667c58b24e76e01/concept-core-ai/experiments/exp001/spec.md)、[decisions.md](https://github.com/buncho-bro/concept-core-ai/blob/e9791b236e2c2618ed77e031e667c58b24e76e01/concept-core-ai/experiments/exp001/decisions.md)。実行コミット `e9791b236e2c2618ed77e031e667c58b24e76e01`。
- 正式結果: [PR #3](https://github.com/buncho-bro/concept-core-ai/pull/3) の head `d5c5d6b4e814d622ec8964dd2836fc2502184c23` に公開された `concept-core-ai/experiments/exp001/run_review/baseline_001_publication/`。PR #3 は `main` の `ab614500328c08e473abc9c6a9541b5c263b3dbe` にマージ済み。下記リンクは内容を固定するためPR headのコミットを指す。
- 主要証拠: [RUN_SUMMARY.md](https://github.com/buncho-bro/concept-core-ai/blob/d5c5d6b4e814d622ec8964dd2836fc2502184c23/concept-core-ai/experiments/exp001/run_review/baseline_001_publication/RUN_SUMMARY.md)、[RUN_MANIFEST.json](https://github.com/buncho-bro/concept-core-ai/blob/d5c5d6b4e814d622ec8964dd2836fc2502184c23/concept-core-ai/experiments/exp001/run_review/baseline_001_publication/RUN_MANIFEST.json)、[aggregate_metrics.json](https://github.com/buncho-bro/concept-core-ai/blob/d5c5d6b4e814d622ec8964dd2836fc2502184c23/concept-core-ai/experiments/exp001/run_review/baseline_001_publication/aggregate/aggregate_metrics.json)、[baseline_manifest.json](https://github.com/buncho-bro/concept-core-ai/blob/d5c5d6b4e814d622ec8964dd2836fc2502184c23/concept-core-ai/experiments/exp001/run_review/baseline_001_publication/aggregate/baseline_manifest.json)、[report.md](https://github.com/buncho-bro/concept-core-ai/blob/d5c5d6b4e814d622ec8964dd2836fc2502184c23/concept-core-ai/experiments/exp001/run_review/baseline_001_publication/aggregate/report.md)。以下ではこれらを順に `RUN_SUMMARY`, `RUN_MANIFEST`, `aggregate_metrics`, `baseline_manifest`, `aggregate report` と呼ぶ。
- 個別証拠: PR内の `artifacts/exp001-seed-<seed>-attempt-01.zip`（1001–1005）。`ZIP::evaluation/summary.json`、`ZIP::evaluation/distance_{initial,final}.json`、`ZIP::training.csv`、`ZIP::reconstruction_losses.json`、`ZIP::reconstruction.npz`、`ZIP::reconstruction.png`、`ZIP::metadata.csv`、`ZIP::evaluation/pca_{initial,final}/pca_2d_{color,shape}.png` を参照した。5 ZIPは `RUN_MANIFEST` に記されたサイズと一致する公開コピーである。

## 読む順序

1. [RESULT_SUMMARY.md](RESULT_SUMMARY.md): 正式判定と全体像。
2. [COLOR_ANALYSIS.md](COLOR_ANALYSIS.md)、[SHAPE_ANALYSIS.md](SHAPE_ANALYSIS.md): 属性別の観測値と解釈。
3. [CROSS_METRIC_ANALYSIS.md](CROSS_METRIC_ANALYSIS.md): 指標間の一致・不一致、再構成と学習曲線。
4. [LIMITATIONS.md](LIMITATIONS.md): この実験で言えないこと。
5. [EXPERIMENT_002_QUESTIONS.md](EXPERIMENT_002_QUESTIONS.md): **PROPOSED**の検証課題。正式仕様ではない。
6. [ANALYSIS_MANIFEST.json](ANALYSIS_MANIFEST.json): 出典と分析状態の機械可読記録。

## 記述規約

`CONFIRMATORY FINDINGS` は事前登録されたprobe accuracyと標準化潜在距離contrast、およびその正式集約による記述に限る。Pixel baseline、PCA、学習曲線、再構成画像、raw距離から得た説明は探索的・補助的証拠として明記する。因果機構や概念核の成立は観測結果と分ける。
