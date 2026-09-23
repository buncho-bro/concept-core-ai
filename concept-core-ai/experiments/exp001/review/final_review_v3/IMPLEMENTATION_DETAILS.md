# IMPLEMENTATION_DETAILS

承認済み研究条件を満たす範囲で、Codexが決定できる事項:

- Python package、class/function名、CLI、内部helper・testの構成。
- run/aggregateの具体的なディレクトリ名、CSV/JSON/parquet等の保存形式。必須情報と再解析可能性を保持する。
- atomic write、既存run上書き防止、cache、距離計算のchunk size・vectorization。
- 正規幾何と同じinside判定を返すpolygonアルゴリズム。
- PCA図のライブラリ、色、凡例、解像度。科学的三値判定には使用しない。
- 指定済みのSHA-256 seed導出・Train専用scaler・定義済み百分位補間を実現するAPIの書き方。
- 実装・依存ライブラリ版と決定的sample順をmanifestへ記録する方法。
- 小数RGBの16 subpixel算術平均を追加量子化せず保持する具体的な保存形式。

PCG64のseed展開と範囲付き整数変換の選択は、正式CIを変えるためここで決定しない。
