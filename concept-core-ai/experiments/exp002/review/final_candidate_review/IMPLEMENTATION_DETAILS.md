# IMPLEMENTATION_DETAILS

- Python package・関数名・CLI・成果物のファイル形式と配置、atomic write、可視化ライブラリ。
- 同じ画像・数値・pair 集合・乱数呼び出し順を維持するベクトル化、チャンク化、キャッシュ。
- §44–47 の範囲の thread/worker 等の性能設定。formal run 前に wall-clock のみで選び、正式5 run で固定・記録する。
- 依存 version の選定と固定。正式5 run の同一環境要件を満たすこと。
- §24 の Held-out-only descriptive statistics の具体的表示項目と、§36 の absolute error map の保存形式。これらは主判定へ使用しない。

研究条件、成功閾値、承認済み bootstrap stream、loss の画像等重み集計は実装側で変更しない。
