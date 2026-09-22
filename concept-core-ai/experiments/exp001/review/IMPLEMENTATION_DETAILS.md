# IMPLEMENTATION_DETAILS

以下は、研究条件が Human によって確定した後であれば、研究条件へ影響しにくく Codex 側で決定可能な事項である。

1. `generate`、`train`、`analyze`、`run` を分離した CLI とモジュール構成にする。
2. 設定ファイルを schema 検証し、未決定の研究条件には暗黙の default を置かず、欠落時に実行を停止する。
3. run directory は新規作成のみ許可し、既存 run の上書きを拒否する。書き込みは一時ファイルからの atomic rename を用いる。
4. CSV は UTF-8、JSON は machine-readable な固定 key、epoch と latent index は 0/1 始まりを文書化して統一する。
5. `sample_id` を全成果物の結合 key とし、重複・欠損・split 重複を検査する。
6. checkpoint loader は architecture/config の不一致を検出し、silent fallback を行わない。
7. 学習コードから評価メタデータへ到達できないこと、同一承認済み設定と seed で metadata が一致すること、split が排他的かつ全件を覆うことを自動テストする。
8. 解析は保存済み checkpoint と metadata だけから再実行可能にし、解析の再実行で Autoencoder の重みを変更しない。
9. 異常終了時も run directory、解決済み設定、エラー情報を残し、失敗 run を削除しない。
10. framework 固有のファイル配置や内部クラス名は Codex が決めてよいが、数式的なモデル構造、前処理、乱数、学習・評価手順は承認済み仕様に従う。
