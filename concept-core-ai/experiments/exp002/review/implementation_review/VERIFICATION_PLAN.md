# VERIFICATION_PLAN

FIX 後、正式 RUN に進まず VERIFY で自動確認する。

1. 正規 attempt 集合を結果に依存せず確定し、余分な同 seed attempt・差し替え・異なる commit/環境・失敗 run が、仕様 §40 の順序どおり扱われること。全 attempt と採否理由を保存する。合成 fixture で恣意的 path 選択が異なる三値判定を出せないこと。
2. 性能設定が最初の formal RUN 前に固定されたことを検証でき、runner が一致しない／事後変更した設定を拒否すること。5 run 間の一致だけでなく、凍結済み設定との一致を確認する。
3. 既存の split・leakage・loss・checkpoint・probe・distance・bootstrap・gate・status・artifact integrity の oracle と統合テストを再実行する。Exp001 source と正式仕様の不変性を差分で確認する。
4. 非formal fixture のみ使用し、正式 seed による学習・結果生成・正式集約を実行しない。修正後の VERIFY receipt と source fingerprint を記録する。
