# IMPLEMENTATION_DETAILS

以下は研究条件を固定した後、Codex が決定・記録できる。

- Python package、クラス／関数名、CLI、成果物の具体的なディレクトリ・JSON/CSV 等の形式。
- 同じ数学的結果を保つ距離計算のチャンク化、ベクトル化、キャッシュ、atomic write、図の描画ライブラリ。
- §42–45 に収まる CPU thread 数・DataLoader worker 数等の性能設定。正式開始前に wall-clock だけで選び、5 run に同一設定を適用して保存する。
- 実行環境の依存 version の固定と記録。ただし正式集合内で一致させる。
- 代表例の画像形式および absolute error map の表示形式。入力、initial/final 再構成と対応する誤差が追跡可能であること。

NB-002-01/02 の数式上の選択を implementation detail として埋めてはならない。
