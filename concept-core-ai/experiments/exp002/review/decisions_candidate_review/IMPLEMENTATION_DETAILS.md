# IMPLEMENTATION_DETAILS

- 文書の見出し・引用・リンク・コードブロックの表示形式は研究条件を変えずに整えられる。
- §31 の性能設定は最終候補仕様 §44–47 の範囲で実装側が選択できる。wall-clock だけで正式実行前に固定し、5 run に同じ設定を使う。
- ファイル形式、CLI、図表、キャッシュ等は数学的実験と成果物の追跡可能性を維持する限り実装側で決められる。

候補 Decision を `APPROVED` とみなすこと、閾値・loss 集計・bootstrap stream を実装側で変更することは implementation detail ではない。
