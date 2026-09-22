# PLAN

現在の `spec.md` を変更せずに進める場合でも、AGENTS.md のワークフローに従い、**B-01〜B-08 が Human により決定され `spec.md` に反映されるまでは IMPLEMENT/RUN へ進まない**。提案だけを根拠に既定値を選ばない。

決定後の実装計画は以下とする。

1. **DECISION gate**: 各 BLOCKER の決定が `spec.md` に存在し、`decisions.md` と矛盾しないことを確認する。
2. **設定と成果物 schema**: 承認済み条件を表す config schema、run directory、manifest、上書き防止を実装する。
3. **データ生成**: 9 組み合わせを承認済み分布で生成し、metadata と split を保存する。画像と metadata の整合性を検証する。
4. **モデルと学習**: 承認済み Autoencoder、前処理、損失、optimizer、停止規則を実装する。学習前 checkpoint を保存してから訓練し、ログと最終 checkpoint を保存する。
5. **潜在抽出**: 承認済み split と initial/final Encoder について latent を抽出し、`sample_id` で評価 metadata と結合する。
6. **解析**: 同一の承認済み手順で PCA、距離解析、線形プローブ、未学習モデル、Pixel baseline を実行する。Autoencoder へ解析勾配を返さない。
7. **VERIFY**: label leakage、再生成、split 排他性、checkpoint round-trip、成果物 schema、既存 run 非上書きを自動テストする。小規模 smoke run は本実験 run と分離して保存する。
8. **RUN**: 承認済み seed と条件を変更せずに実行し、成功・失敗を問わず全 run を保存する。
9. **ANALYZE**: 数値的な観測事実と科学的解釈を分けた `report.md` を作成する。成功条件の判定と解釈は Human の確認対象とする。

現仕様のまま今すぐ可能なのは、研究条件に値を与えない CLI/config schema、上書き防止、成果物 writer などの非研究的 scaffolding までである。ただし、それらも正式な DECISION の後に着手するのが AGENTS.md の定める順序に最も整合する。
