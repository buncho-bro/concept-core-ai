# VERIFICATION_PLAN

正式承認・仕様反映後、IMPLEMENT/VERIFY で少なくとも次を自動確認する。

- 正式 `spec.md` が承認対象の最終候補と一致し、承認記録・git commit・5 run の設定を追跡できること。`decisions.md` は仕様を上書きしない。
- Seen/Held-out 組み合わせ、800/100/100 と 100/900 の split、Reserved 非使用、学習・probe 選択・scaler・threshold への Held-out leakage がないこと。
- per-image-first balanced loss、zero baseline、Seen Test gate の手計算照合と 4/5・中央値境界。
- initial/final の比較、Seen Train scaler、Seen Validation のみの C 選択、Held-out probe delta、pixel controls が仕様どおりであること。
- standardized cross-distance、Seen-only/cross の独立 RNG sub-seed、sample bootstrap、600→300 の cross 抽出順、1000 iterations、CI 補間・950 境界。
- formal 5 run の同一 commit/環境、run status と evaluation flags の分離、SUCCESS/INCONCLUSIVE/NO_EVIDENCE/NOT_EVALUATED の優先順位と閾値境界。
- 研究結果後に条件を変更せず、失敗 run と secondary controls を保存・報告すること。
