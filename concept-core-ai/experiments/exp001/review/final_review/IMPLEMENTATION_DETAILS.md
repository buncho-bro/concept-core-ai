# IMPLEMENTATION_DETAILS

研究条件確定後、以下は研究条件を変更せずCodex側で決定できる。

- CLIと内部モジュール構成
- 成果物のディレクトリ名とファイル分割
- CSV/JSON等の保存形式
- pairwise距離計算のchunk sizeやvectorization
- raw pairを保存するか、保存済みlatentから再計算するか
- plotの色、凡例、解像度など成功判定に関係しない表示
- atomic write、上書き防止、failure log
- schema validationと内部クラス名
- 十分な精度を保つ浮動小数点シリアライズ
- dependency/version、device、決定性設定、成果物hashなどの追加manifest
- 固定sample選択規則。ただし規則は結果を見る前に決め、記録すること

bias、初期化、latent標準化、bootstrap方式、seed集合など、測定結果を変える事項はimplementation detailとして扱えない。
