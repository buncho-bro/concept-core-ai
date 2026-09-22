# RESOLVED_BLOCKERS

## B-01 — NOT_RESOLVED

SUCCESS条件そのものは具体化されているが、以下が未確定である。

- 5 seedで何を変動させるか。全用途seedを変えるのか、dataset/splitを固定してmodel seedだけ変えるのかで判定対象が変わる。
- 使用する5個のmaster seedまたは導出規則。
- `distance_contrast_final > distance_contrast_initial` が、それぞれの中央値の比較か、seedごとの差の中央値が正であることか。
- INCONCLUSIVEとNO_EVIDENCEの数値的な境界。
- seed runの失敗または欠損がある場合の判定方法。

したがってSUCCESSは機械判定可能だが、Experiment全体の三値判定はまだ機械化できない。

## B-02 — NOT_RESOLVED

RGB、位置、大きさ、回転、塗り、supersampling倍率、clipping禁止は反映されている。

一方、以下のデータセット条件が一意でない。

- 256×256から64×64へ縮小するフィルタ
- 三角形・四角形の頂点生成とpixel-center規約
- rasterizerの境界処理
- `U(0,360)` の端点規約と乱数実装

特に縮小フィルタはアンチエイリアス、foreground面積、Pixel baseline、再構成損失を変える。

## B-03 — RESOLVED

各組み合わせ800/100/100、層化単位、shuffle順序、`split_seed`、排他性、全件網羅、各splitの役割が定義されている。

TrainはAutoencoder学習、Validationは承認済み設定選択、Testは最終評価専用であり、役割の矛盾はない。

## B-04 — NOT_RESOLVED

層構成、activation、latent次元、正規化層・dropout不使用は確定している。

ただし、以下が未指定である。

- Conv/Linearのbias有無
- weight/bias初期化方式
- parameter dtypeとmixed precision使用可否

これらはinitial Encoder性能と学習結果を変えるため、framework defaultで補うことはできない。

## B-05 — RESOLVED

MSE mean、Adamの主要パラメータ、50 epoch、batch size、DataLoader、scheduler・early stopping・gradient clipping不使用、解析対象を`final.pt`とすることが一致して定義されている。

Validationは損失記録だけに使用され、Autoencoderの更新・checkpoint選択には使われない。

## B-06 — NOT_RESOLVED

Trainでprobe学習、ValidationでC選択、Testで最終評価という分離は正しく、Test漏洩はない。initial/finalにも同じ候補Cと選択規則が適用される。

ただし、以下が未指定である。

- latentをprobe前にTrain統計で標準化するか
- 標準化しない場合、それを明示的な研究条件とするか
- logistic regressionのintercept、class weight
- solver非収束時の扱い
- `balanced_accuracy`がどのsplitの値か

特にlatentの尺度はL2正則化とC選択へ直接影響する。

## B-07 — NOT_RESOLVED

以下は一意に定義されている。

- initial/finalそれぞれ自身のTrain latent統計を使う
- `std < 1e-8` の次元を除外する
- Testの全404,550ユニークペアを使う
- aggregateはペア集合を結合して再集計する
- raw Euclideanは補助解析とする

一方、sample単位bootstrapは一意に実装できない。

- 900サンプルを復元抽出したとき、重複sampleを別出現として扱うか
- 同じsampleが複数回抽出された場合のゼロ距離ペアを含めるか
- sample multiplicityをpair weightへどう変換するか
- percentile/basic/BCaのどの95% CIを使うか
- `std_train`および距離のstandard deviationで`ddof=0/1`のどちらを使うか

異なる実装でCIが変わるため、評価方法として未解消である。

## B-08 — NOT_RESOLVED

Pixel baseline自体は必須化され、特徴量、Train標準化、C候補、Train/Validation/Testの用途が定義されている。

ただしPixel特徴は標準化される一方、latent probeの標準化が未指定である。同じL2正則化とC gridを使っても特徴量尺度が異なるため、公平で一意な比較にならない。

Pixel baselineは成功条件に使わないためSUCCESS判定には直結しないが、controlとしての解釈が実装依存になる。
