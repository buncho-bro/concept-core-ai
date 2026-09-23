# RESOLVED_BLOCKERS

| 項目 | 判定 | 理由 |
| --- | --- | --- |
| NB-01 | RESOLVED | master seed `1001`〜`1005`、用途別SHA-256導出、6乱数系列の変動、同一commitでの正式5 run、runとExperimentの成果物分離が定義された。新しい§18/§21が失敗時の判定順序も定める。 |
| NB-v2-01 | RESOLVED | `VALID`/`INVALID`/`EXPERIMENTAL_FAILURE`と評価flagを分け、同一commitのnon-INVALID runが5件未満なら`NOT_EVALUATED`、主要指標欠損なら`INCONCLUSIVE`、CI/controlのみの失敗なら科学的判定を続ける。§21の優先順序により指定7ケースのExperiment-level状態は一意。 |
| NB-v2-02 | NOT_RESOLVED | 連続PCG64 stream、900回×1000反復、保存済みTest順、percentileの線形補間が追加された。しかし`analysis_seed`からのPCG64内部状態の作り方と、64-bit出力を`[0,900)`へ変換する方法が未指定。同じseedから複数の妥当なbootstrap index列・CIを生成できる。 |
| B-01 | RESOLVED | `probe_delta_A`、`distance_contrast_A`、`distance_delta_A`、4/5条件、中央値の閾値、完全指標がある場合の三値分類、指標欠損時の優先判定が機械的に定義された。 |
| B-02 | RESOLVED | RGB分布、位置、外接円半径、`[0°,360°)`、座標・幾何・境界・16 subpixel算術平均・clipping禁止が定義されている。追加の整数丸めは承認されていない。 |
| B-03 | RESOLVED | 9組み合わせ×1000、各800/100/100、`split_seed`、splitの排他・網羅、Train/Validation/Testの用途が定義されている。 |
| B-04 | RESOLVED | 層構成・bias・latent・初期化対象と方式・biasゼロ・FP32・AMP/FP16/BF16/TF32無効・BatchNorm/Dropout不使用が定義されている。 |
| B-05 | RESOLVED | 再構成のみ、MSE mean、Adam設定、50 epoch、batch 128、`loader_seed`、初期/最終checkpoint、Validationの用途が定義されている。 |
| B-06 | RESOLVED | initial/finalの凍結Encoder、各Trainのみでfitする別scaler、ddof=0、L2多項logistic regression、収束判定、ValidationでC選択、Test最終評価、ラベル順と指標が定義された。主要probe失敗時のExperiment判定も定義された。 |
| B-07 | NOT_RESOLVED | Test全404,550 pair、4カテゴリ、Train統計、ddof=0、aggregate、sample単位bootstrapのinstance/pair規則とpercentile算出式は確定した。残るindex列の一意性はNB-v2-02と同じ問題である。 |
| B-08 | RESOLVED | 画像統計とraw pixelの2 control、Train標準化、ddof=0、classifier条件、C選択、Test隔離、指標がprobeと整合する。control失敗のみで科学的三値判定を停止しないことも明記された。 |

前回reviewの文言は履歴として扱い、正規仕様の判定を上書きしない。
