# IMPLEMENTATION_DETAILS

承認済み条件を守る範囲でCodexが決定できる事項:

- package構成、class/function名、CLI、内部helper、test構成。
- run/aggregateの具体的なファイル名・配置、CSV/JSON/parquet等の保存形式。必須情報とTest順序を再構成可能にする。
- atomic write、上書き防止、cache、pair距離計算のbatch/chunkサイズ。
- 承認済み幾何と同じinside判定を返すpolygon判定アルゴリズム。
- PCA図のライブラリ、配色、凡例、解像度。三値判定へ使用しない。
- 正式5 runに共通して用いるNumPy版の依存関係固定と、その版・environmentをmanifestへ記録する方法。版をrun間で混在させない。
- 承認済みNumPy APIを呼び出すコード構造と、乱数index列を追加監査用artifactへ保存するかどうか。
- 16 subpixel平均の小数RGBを追加量子化せず保持する保存形式。

これらの選択は実行前に固定し、数値結果が仕様から逸脱していないことを検証する。
