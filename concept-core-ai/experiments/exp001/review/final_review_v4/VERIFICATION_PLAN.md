# VERIFICATION_PLAN

IMPLEMENT後に次を自動検証する。

1. **seed/正式集合**: master seedが1001〜1005の5個だけで、6目的のSHA-256 seed導出が固定テストベクトルと一致する。同一commit・同一NumPy版のnon-INVALID runだけを正式集合に入れ、run単位で科学的三値判定を出さない。
2. **bootstrap RNG**: `Generator(PCG64(analysis_seed))`を直接生成し、`rng.integers(low=0, high=900, size=900, endpoint=False, dtype=numpy.int64)`を反復0〜999で各1回呼ぶ。同じseed・NumPy版・Test順序から最初のindex vectorが一致し、全1000 vector・bootstrap mean列・CIも一致する。streamを再seedせず、別RNG/APIや独自整数写像を使用しない。
3. **bootstrap統計**: 保存済みTest順の900 sampleを復元抽出し、出現ごとのinstanceを区別する。同一original sample_id間pairを除外し、異なるsample間multiplicityを保持する。pair直接bootstrap・scaler再fit・latent再抽出をしない。`Q(0.025)`/`Q(0.975)`の線形補間、950/949有効反復境界、`BOOTSTRAP_CI_FAILED`を確認する。
4. **run状態と集約境界**: 5 VALID＋完全指標は通常三値、4 VALID＋1 INVALIDは`NOT_EVALUATED`、4 VALID＋1 EXPERIMENTAL_FAILUREは`INCONCLUSIVE`、1 PROBE_FAILEDまたは1 DISTANCE_FAILEDは`INCONCLUSIVE`。BOOTSTRAP_CI_FAILEDだけなら`DISTANCE_CI_INCOMPLETE`、PIXEL_BASELINE_FAILEDだけなら`CONTROL_INCOMPLETE`を報告し三値判定を継続する。複数flagと判定優先順もtable-driven testで検証する。
5. **成功条件**: 属性ごとのprobe delta、final accuracy、distance contrast/delta、4/5条件、各中央値を成果物から再計算する。`>0`・`>=0.10`・`>=0.70`・中央値`>0`の等号境界、3/5と4/5、片属性だけの成功を検証する。
6. **dataset/rasterization**: 9組み合わせ各1000、RGB値・独立channel変動・中心・外接円半径・`[0°,360°)`、pixel中心・y軸、16 subpixel位置・算術平均・円/三角/四角の境界、非clipping、追加量子化なしをfixtureで検証する。
7. **split/leakage**: 各組み合わせ800/100/100、split排他と全件網羅、全splitに9組み合わせ、generation/split seed分離を確認する。Testを設定選択へ、評価ラベルをAutoencoder入力・損失・勾配・更新へ使わない。
8. **model/training**: 全層・shape・bias・初期化・parameter数、FP32/AMP等無効、MSE mean、Adam全設定、50 epoch・batch 128、scheduler/early stopping/gradient clipping/latent regularizationなし、update前initialと50 epoch後finalを確認する。Validationはmonitoringのみ。
9. **latent/probe/distance**: initial/final×3 splitのlatentを全件保存する。状態別Train-only scaler、ddof=0、near-zero除外、凍結Encoder、指定classifierと収束C選択、Test隔離・class順・必須metricsを確認する。Test pairは404,550、4カテゴリ件数44,550/90,000/90,000/180,000、aggregate結合後再計算、Train統計による標準化、raw補助距離を確認する。
10. **Pixel controlと再解析**: 7統計特徴と12288 raw特徴、foreground・ddof=0、Train-only標準化、probeと同じclassifier/C選択を確認する。Pixel controlはAutoencoder学習へ影響しない。run-levelの設定・metadata・checkpoint・log・latent・probe・距離・bootstrap・control・status/flags、aggregate-levelのseed・commit・NumPy版・各delta・中央値・4/5・最終判定を再計算可能にする。
