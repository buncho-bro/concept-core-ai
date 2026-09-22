# VERIFICATION_PLAN

IMPLEMENT後、承認済み条件に対し次を自動検証する。

1. **seed導出と再現性**: 正式master seedが1001〜1005の5個で重複がない。6目的のSHA-256導出値が固定テストベクトルと一致し、同一commit・環境・seedから画像、split、initial重み、loader順、解析結果が再現する。
2. **dataset generation**: 9組み合わせ各1,000件。RGB基準値・channel変動・整数位置と外接円半径・`[0°,360°)`・頂点座標・pixel中心・y軸方向・16 subpixelのinside判定・box平均・画像値の承認済み保存規約・非clippingを検証する。
3. **split**: 各組み合わせのTrain/Validation/Testが800/100/100で相互排他かつ全件網羅。各splitに9組み合わせすべてがあり、`split_seed`が生成乱数系列から独立する。
4. **label leakage**: Autoencoderの入力、損失、勾配、parameter updateへ評価ラベルとmetadataが渡らない。probeと距離カテゴリでのみ必要ラベルを使用する。
5. **model・initialization・precision**: Encoder/Decoderの全層、shape、bias、ReLU/Sigmoid、Kaiming/Xavier対象、biasゼロ、parameter数、`model_seed`依存を確認する。parameter・activation・lossはFP32、AMP/FP16/BF16/TF32無効、BatchNorm/Dropoutなし。
6. **training・checkpoint**: MSE mean、Adam設定、50 epoch、batch 128、loader seed、scheduler/early stopping/gradient clipping/latent regularizationなし。`initial.pt`はupdate前、`final.pt`は50 epoch後。Validation/Testは更新やcheckpoint選択に使わない。
7. **latent completeness**: initial/final × Train/Validation/Testの6集合が全sampleに対応し、`sample_id`の欠損・重複・split跨ぎがない。
8. **probe preprocessing・C selection**: initial/final別にTrain latentだけでmean/std（ddof=0）をfitし、`std < 1e-8`を除外する。classifier設定、class順、各Cの収束判定、Validation最大・同率最小C、指定metricsを確認する。Testをscaler fitやC選択に使わず、probe gradientはEncoderへ返さない。
9. **距離とaggregate**: Testのunordered unique pairは404,550件。4カテゴリ件数は44,550 / 90,000 / 90,000 / 180,000。自己pairなし。aggregateは集合結合後に再集計。initial/final別Train統計、ddof=0、near-zero除外、standardized primaryとraw secondaryを確認する。
10. **bootstrap**: 900 sampleの復元抽出を1000回実施し、出現instance別identity、同一original sample間pair除外、multiplicity、pair直接再標本化禁止、fixed Test latent、fixed Train scaler、empty category、950有効反復閾値、承認済み百分位規約を検証する。同一入力と`analysis_seed`からCIが再現する。
11. **Pixel baseline**: 7画像統計特徴（RGB stdのddof=0とforeground定義）、12288 raw特徴、両者のTrain標準化・near-zero除外を確認する。probeと同じclassifier/C/収束/選択/metric条件でTestを最終評価だけに使用し、Autoencoder学習への影響がない。
12. **run status**: INVALID、EXPERIMENTAL_FAILURE、probe・bootstrap・Pixel baseline FAILED、NOT_EVALUATEDの全境界を承認後の規則に従ってtable-driven testで検証する。失敗runを削除・上書きしない。
13. **Experiment集約**: 同一commitの正式5 seedだけをmanifestで束ね、runでは三値判定しない。probe delta、distance contrast/delta、各中央値、4/5条件、属性OR、SUCCESS/INCONCLUSIVE/NO_EVIDENCE/NOT_EVALUATEDの分岐を成果物から再計算する。
14. **成功境界**: `>0`と`>=0.10`/`>=0.70`、4/5と3/5、中央値がちょうど閾値、片属性のみ成功、評価欠損の各例で機械判定を検証する。
15. **再解析**: run-levelの設定・metadata・checkpoint・log・latent・probe・距離・CI・Pixel baseline、Experiment-levelのseed・commit・status・集約指標から、同じ報告値を再構成できる。
