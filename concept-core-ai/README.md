# Concept-core AI — Experiment 001

承認済み Experiment 001 の実装です。正規仕様は GitHub の
[spec.md](https://github.com/buncho-bro/concept-core-ai/blob/207bee36f2a5b1b57de2d73d582ef9f890dbe855/concept-core-ai/experiments/exp001/spec.md)、
APPROVED decisions、final_review_v4 の順で参照しました。
今回の範囲は IMPLEMENT + VERIFY です。正式 baseline は未実行です。

## セットアップ

Python 3.12 を使用します。Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-lock.txt
.\.venv\Scripts\python.exe -m pip install -e '.[verify]'
```

NumPy は 2.3.5 に固定しています。依存関係の固定ファイルは今回検証した Windows CPU 環境のものです。
GPU 環境でも FP32、AMP/TF32 無効、決定的アルゴリズムを指定しますが、今回の検証対象は CPU です。

## VERIFY — 正式実験を実行しない

未使用の出力ディレクトリを指定します。

```powershell
.\.venv\Scripts\python.exe -m exp001 verify --output .verify-tmp/check-001
```

テスト結果、JUnit XML、環境・実装ハッシュを含む `verification.json` を保存します。
同じ出力ディレクトリを再使用できません。再検証時は新しい名前を指定してください。
テスト内の小規模学習・合成データ評価・集約fixtureは、正式実験の科学的結果ではありません。

## RUN — 後続の MODE: RUN 専用

以下は実行手順の説明です。今回の IMPLEMENT では実行していません。
まず実装と既存のローカル配置変更をレビューし、使用するコードをコミットして作業ツリーをクリーンにしてください。
同じ実装・環境で VERIFY が通っていることが必要です。

```powershell
.\.venv\Scripts\python.exe -m exp001 run-one --master-seed 1001 --output runs/seed-1001-attempt-01 --verification .verify-tmp/check-001/verification.json
```

同一コミット・同一環境のまま 1002、1003、1004、1005 に対してそれぞれ明示的に実行します。
`run-one` は指定seedの9,000画像生成、50 epoch学習、全評価を行います。所要時間・メモリは環境に依存します。
研究条件を変更するCLI引数はありません。`--device cuda` は利用可能なGPU環境でのみ使用できます。

## 集約と再解析

同一コミット・同一NumPy版の、採用する5つのrunディレクトリを明示します。
再試行の選択をプログラムが自動で行うことはありません。

```powershell
.\.venv\Scripts\python.exe -m exp001 aggregate runs/seed-1001-attempt-01 runs/seed-1002-attempt-01 runs/seed-1003-attempt-01 runs/seed-1004-attempt-01 runs/seed-1005-attempt-01 --output aggregate/baseline-01
.\.venv\Scripts\python.exe -m exp001 reanalyze runs/seed-1001-attempt-01 --output aggregate/reanalysis-1001-01
```

再解析は保存された画像・潜在表現・metadataを使用し、Encoderを再学習・再実行しません。
出力は新しいディレクトリへ保存します。既存runやその集約結果を上書きしません。

## 成果物

runディレクトリには次を保存します。

- `configuration.json`: 全研究設定、seed、git commit、NumPy/依存版、実装ハッシュ、parameter数。
- `metadata.csv`, `split.npz`, `images.npy`: 全sample、分割、量子化していないRGB。配列の画像順はmetadata行順。
- `initial.pt`, `final.pt`, `training.csv`: 更新前／50 epoch後の状態、Adam状態、epochごとの損失。
- `latent/{initial,final}_{train,validation,test}.npz`: sample ID付き潜在表現。各splitはsample ID昇順。
- `reconstruction_losses.json`, `reconstruction.npz`, `reconstruction.png`: 各split損失とTest先頭9件の固定比較。
- `evaluation/probe_*.json`, `pixel_*.json`: Train scaler、除外次元、全C収束状態、選択C、係数、class順、予測、必須指標。
- `evaluation/distance_*.json`, `pairs_*.npz`: Train scaler、全pair、カテゴリと結合統計、raw/標準化距離。
- `evaluation/bootstrap_*.npz`: 全1,000抽出列・平均列、Test ID順、カテゴリ順。
- `evaluation/pca_*`: 2D/3D座標、成分、平均、説明分散、色／形の図。同一状態・次元の表示に同じ座標を使用。
- `status.json`, `failure.json`（失敗時）, `report.json`, `integrity.json`: 実行状態、複数評価flag、失敗記録、成果物のハッシュ。

run開始時の状態は `INVALID / complete=false` です。強制終了でも完了と誤認しません。
学習の数値的失敗は `EXPERIMENTAL_FAILURE`、技術的例外や中断は `INVALID` として保存します。
失敗・中断したディレクトリを削除せず、新しい名前で再試行してください。

集約では `baseline_manifest.json`、`aggregate_metrics.json`、`report.md` を保存します。
正式集合、各delta、中央値、4/5条件、run間変動、Pixel control要約、警告を記録します。
個々のrunは科学的三値判定を出しません。

## 実装・検証記録

`experiments/exp001/implementation_review/` に計画、GitHub参照コミットとblob ID、検証対応表、結果を保存します。
実装の追加先は現在のローカル作業ディレクトリです。作業前から存在する文書の配置変更は変更していません。
