# VERIFICATION_PLAN

IMPLEMENT 前に NB-002-01/02 の承認済み決定を仕様へ反映する。以下は IMPLEMENT 後の自動検証項目。

- 5 master seed と `exp002|` SHA-256 用途別導出、同一 seed の再現、formal set の commit・依存 version・device class・thread/worker 設定の一致。
- 9,000 件・各組み合わせ 1,000 件、生成画像の座標・色・4×4 rasterization、ID の一意性と追加量子化なし。
- Seen Train 4,800、Seen Validation 600、Seen Test 600、Held-out Test 300、Reserved 2,700 の排他性・全件網羅。hold-out 組み合わせは学習・validation・scaler/C 選択・gate に入らず、Reserved は正式解析に入らない。
- Autoencoder の architecture、初期化、FP32 と AMP/FP16/BF16/TF32 無効、initial は更新前・final は 50 epoch 後、評価ラベルが学習経路へ流れないこと。
- 承認後の balanced MSE 集計式を、手計算できる小バッチで Train・評価・zero baseline・ratio まで検証。
- frozen initial/final Encoder、Seen Train のみの別 scaler（ddof=0、閾値）、候補 C の収束扱いと Seen Validation のみの選択、Held-out Test を選択へ使わないこと。Pixel controls に同条件を適用。
- Seen-only 179,700 pair と 4 カテゴリ `29,700/30,000/30,000/90,000`、cross 180,000 pair と 3 カテゴリ各 60,000。self/重複なし、primary は Seen-Train-standardized Euclidean、raw は secondary。
- Cross bootstrap の 600→300 順の `Generator(PCG64(analysis_seed))` 抽出、同一 Generator 1000 反復、出現 multiplicity、pair 直接再抽出・再 fit なし、属性別有効反復数、線形補間 percentile、950 境界。承認後の Seen-only CI も独立に検証。
- 9 代表例の Test 内最小 sample ID、入力・initial/final 再構成・誤差と per-sample 指標の対応。
- run-level status/flags と experiment-level 判定の分離。0.80/1.0 gate、4/5、0.05、0.70、正負ゼロ、missing primary evidence、INVALID、EXPERIMENTAL_FAILURE、CI/control warning の境界テスト。
- Run-level 成果物だけから各データ・checkpoint・latent・probe・distance・bootstrap を追跡でき、Experiment-level 成果物だけから正式集合と判定を再計算できること。
