# IMPLEMENTATION_DETAILS

以下は承認済み研究条件を守る範囲でCodexが決定できる。

- Python package、class・function名、CLI構造、モジュール境界。
- 成果物の具体的なディレクトリ名と、CSV/JSON/parquet等の保存形式。必須fieldと再解析可能性を保つ。
- atomic write、既存runの上書き防止、cache戦略、距離計算のbatch/chunkサイズ。
- 同じ幾何判定を返すpolygon内部判定の実装と、16 subpixel平均を行う内部計算方式。
- 算術平均で得た小数RGBを追加量子化せず保存・読込できる画像表現。数値の丸め誤差はFP32入力条件と再現性要件の範囲に収める。
- 可視化ライブラリ、配色、凡例、表示解像度。PCA図は成功判定に用いない。
- テストコードの構成、schema validation、manifest・ログの追加項目。
- 承認済み分布を実現する画像生成・split・DataLoader用乱数ライブラリとバージョンの選択。実装後は同一commit・環境・seedでの再現を検証する。
- 再構成比較画像のsample選択規則。結果を見る前に決めて記録し、成功判定に利用しない。

bootstrap CI算出規約と評価不能runの科学的分類は研究結果を変えるため、この一覧に含めない。
