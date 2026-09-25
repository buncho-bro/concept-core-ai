# TRACEABILITY

| 仕様→実装 | 主な根拠 | 判定 |
| --- | --- | --- |
| §3–10 seed・生成・split・Reserved | `config.py`、`data.py`、`runner.py:_execute_attempt`。Exp001 `generate_metadata`/`rasterize`/`ImageDataset` を再利用 | PASS |
| §11–15 AE loss・zero・gate | `reconstruction.py`、`training.py`、`runner.py:export_states`、`aggregation.py:reconstruction_gate` | PASS |
| §16–21 probe・pixel control | `evaluation.py`、`runner.py:evaluate_saved`。Exp001 `TrainScaler`/`select_classifier`/`pixel_features` を再利用 | PASS |
| §22–34 距離・bootstrap | `distance.py`。Exp001 pair/statistics/instance mean/percentile helper は 900 件固定の入口を呼ばずに再利用 | PASS |
| §35–36 代表成果物 | `data.py:representative_indices`、`visualization.py:reconstruction_artifacts` | PASS |
| §37–43 run status・三値判定 | `runner.py:_execute_attempt`、`aggregation.py:aggregate_records`。7段の順序と閾値は一致 | PASS（正式 attempt 選定は REV-002-01） |
| §44–50 性能・formal 集合 | `performance.py`、`runner.py:run_one`、`aggregation.py:_same_required_environment` | FAIL（REV-002-01/02） |

Implementation→Specification: Exp002 は Exp001 の生成、モデル・初期化・精度制御、Adam/checkpoint、scaler/probe/pixel、pair/CI、PCA、artifact I/O を import する。Exp001 の 900 件固定 `bootstrap` / `analyze_distance` および 800/100/100 split は呼ばず、Exp002 専用処理に置換する。PR #6 の差分は Exp002 の新規実装・テスト・実装者報告と `pyproject.toml` の CLI 追加のみで、Exp001 source、正式 Exp002 仕様／Decision、review history、依存 version の変更はない。

Source→Tests: 主要計算の独立 oracle と不足箇所は `TEST_AUDIT.md` に整理した。テスト通過数だけでは REV-002-01/02 を覆せない。
