# Experiment 001 Decisions

この文書は、Experiment 001についてHumanが承認した研究条件を記録する。

`spec.md` は実装時の正規仕様とし、本書はその決定根拠および変更履歴を保持するために使用する。

---

# DEC-001 — Reconstruction Loss

Status: SUPERSEDED  
Superseded by: DEC-B05

旧提案ではAutoencoderの再構成損失としてMSEを使用することのみを決定していた。

この内容は現在、DEC-B05の学習条件に統合されている。

---

# DEC-NB01 — Formal Baseline Run Set and Experiment-Level Evaluation

Status: APPROVED

Experiment 001の正式baselineは、5つのmaster seedによる5 runで構成する。

失敗runおよびExperiment-level状態遷移の詳細については、後続の `DEC-NB-v2-01` を優先する。

## Formal master seeds

```text
1001
1002
1003
1004
1005
```

この5 seedは実行前に固定し、結果確認後に変更してはならない。

---

## Seed derivation

各runではmaster seedから用途別seedを決定的に導出する。

対象:

```text
generation
split
model
loader
probe
analysis
```

導出方法:

```text
SHA-256(
  "exp001|" + master_seed + "|" + purpose
)
```

SHA-256 digestの先頭32 bitをunsigned integerとして使用する。

したがって各runには、

```text
master_seed
generation_seed
split_seed
model_seed
loader_seed
probe_seed
analysis_seed
```

が存在する。

処理順序によってseed値が変化してはならない。

---

## 5 runで変動させるもの

5つの正式runでは、master seedから派生するすべての乱数系列を変化させる。

したがってrun間では、

- 画像生成
- dataset split
- model initialization
- DataLoader順序
- probe関連乱数
- analysis / bootstrap乱数

がそれぞれ変化する。

Experiment 001における再現性とは、

> 実験手続き全体を異なる乱数条件で繰り返しても同様の構造形成傾向が観測されるか

を意味する。

---

## Run-levelとExperiment-levelを分離する

個々のrunではExperiment全体の、

```text
SUCCESS
INCONCLUSIVE
NO_EVIDENCE
```

を判定しない。

run-level成果物では最低限、

```text
OBSERVATIONS
METRICS
WARNINGS
ARTIFACTS
```

を記録する。

最終科学的判定は、正式5 runを集約したExperiment-level成果物でのみ行う。

---

## Experiment-level成果物

正式5 runの集合と集約結果を保存する。

論理的には以下を区別できる構造とする。

```text
runs/
  <individual runs>

aggregate/
  baseline_manifest
  aggregate_metrics
  report
```

正確なファイル名や配置は実装側で決定してよい。

`baseline_manifest` には最低限、

```text
experiment_id
git_commit

formal_master_seeds:
  - 1001
  - 1002
  - 1003
  - 1004
  - 1005

各runについて:
  master_seed
  run_id
  derived seeds
  status
```

を保存する。

---

## Failure semantics

このDecisionで過去に使用していた「有効run」という表現について、正式なexecution statusおよびExperiment-level判定規則は `DEC-NB-v2-01` により置き換える。

したがって、

```text
4 VALID + 1 EXPERIMENTAL_FAILURE
```

は `NOT_EVALUATED` ではなく、`DEC-NB-v2-01` に従って `INCONCLUSIVE` とする。

---

# DEC-B01 — Success Criteria

Status: APPROVED  
Source: review/BLOCKERS.md#B-01

Experiment 001は概念核の存在を証明しない。

目的は、

> 再構成学習によって、学習前には弱かったcolorまたはshapeに対応する再現可能な規則的潜在構造が形成されたか

を判定することである。

---

## Attributes

```text
color
shape
```

について独立に評価する。

---

## Primary metric

主判定にはlinear probeのTest accuracyを使用する。

各attribute `A`について、

```text
probe_delta_A(seed)
=
final_encoder_test_accuracy_A(seed)
-
initial_encoder_test_accuracy_A(seed)
```

を定義する。

---

## Probe success conditions

attribute Aについて以下をすべて満たすこと。

```text
5 seed中4 seed以上で
probe_delta_A > 0
```

```text
median(probe_delta_A) >= 0.10
```

```text
median(final_encoder_test_accuracy_A) >= 0.70
```

---

## Confirmatory metric

主確認指標にはstandardized Euclidean distanceを使用する。

colorについて、

```text
distance_contrast_color
=
mean(different_color)
-
mean(same_color)
```

shapeについて、

```text
distance_contrast_shape
=
mean(different_shape)
-
mean(same_shape)
```

を定義する。

各seedについて、

```text
distance_delta_A(seed)
=
distance_contrast_final_A(seed)
-
distance_contrast_initial_A(seed)
```

を定義する。

---

## Distance success conditions

attribute Aについて以下をすべて満たすこと。

```text
final Encoderで
5 seed中4 seed以上
distance_contrast_A > 0
```

```text
median(distance_delta_A) > 0
```

---

## SUCCESS

colorまたはshapeの少なくとも一方が、

- Probe success conditions
- Distance success conditions

の両方を満たす場合、

```text
SUCCESS
```

とする。

---

## INCONCLUSIVE

SUCCESSではないが、colorまたはshapeの少なくとも一方について、

```text
median(probe_delta_A) > 0
```

または、

```text
median(distance_delta_A) > 0
```

が成立する場合、

```text
INCONCLUSIVE
```

とする。

主要指標欠損時のINCONCLUSIVE判定については `DEC-NB-v2-01` を適用する。

---

## NO_EVIDENCE

正式5 runすべてで必要な評価が正常に完了し、SUCCESSではなく、colorとshapeの両方について、

```text
median(probe_delta_A) <= 0
AND
median(distance_delta_A) <= 0
```

の場合、

```text
NO_EVIDENCE
```

とする。

NO_EVIDENCEは、

> この実験条件および事前登録した評価方法では、学習による一貫した構造強化を確認できなかった

ことを意味する。

概念核そのものが存在しないことを意味しない。

---

## PCA

PCAは探索的可視化にのみ使用する。

成功判定には使用しない。

---

## Pixel baseline

Pixel baselineは結果解釈用controlとして使用する。

latentがPixel baselineを上回ること自体を成功条件にはしない。

---

## Interpretation constraints

- SUCCESSでも「概念核を発見した」と結論しない。
- colorとshapeの結果を分離して報告する。
- 基準未達結果を実行後に成功として再解釈しない。
- 結果確認後に成功閾値を変更しない。

---

# DEC-B02 — Dataset Generation

Status: APPROVED  
Source: review/BLOCKERS.md#B-02

Experiment 001の人工画像生成条件を以下とする。

---

## Image

```text
width: 64
height: 64
channels: RGB
background: [0, 0, 0]
```

---

## Colors

```text
red:   [230, 25, 25]
green: [25, 230, 25]
blue:  [25, 25, 230]
```

---

## Color variation

各sampleについて、各RGB channelへ独立に、

```text
U_integer(-10, +10)
```

を加える。

foreground RGBは図形描画前にsample単位で一度だけ決定する。

最終RGB値は `[0,255]` に制限する。

---

## Position

```text
center_x = U_integer(26, 38)
center_y = U_integer(26, 38)
```

---

## Size

```text
definition: circumradius_px
size = U_integer(12, 16)
```

円ではradiusそのものを表す。

正三角形・正方形では外接円半径を表す。

---

## Rotation

```text
circle:
  rotation = 0.0

triangle:
  rotation ~ Uniform[0°, 360°)

square:
  rotation ~ Uniform[0°, 360°)
```

360°自体は生成しない。

rotationは実数として保持し、実際に使用した値をmetadataへ保存する。

---

## Coordinate system

最終64×64画像では、

```text
x = 0 ... 63
y = 0 ... 63
```

をpixel center座標とする。

pixel `(x,y)` の領域は、

```text
[x - 0.5, x + 0.5)
×
[y - 0.5, y + 0.5)
```

とする。

y軸は画像下方向を正とする。

---

## Supersampling

4×4 subpixel supersamplingを使用する。

各final pixelについてsubpixel centerを、

```text
x + {-3/8, -1/8, +1/8, +3/8}
y + {-3/8, -1/8, +1/8, +3/8}
```

の全16組み合わせとする。

各subpixelについて図形内部判定を行う。

final pixel RGBは16 subpixelのRGB値の算術平均とする。

一般的な画像resize filterには依存しない。

追加の整数丸め・量子化を研究条件として導入しない。

---

## Circle geometry

中心 `(cx,cy)`、radius=`size` とする。

subpixel `(px,py)` が、

```text
(px-cx)^2 + (py-cy)^2 <= size^2
```

なら内部とする。

境界上もinsideとする。

---

## Triangle geometry

常に正三角形とする。

外接円半径は `size`。

頂点角度は、

```text
rotation
rotation + 120°
rotation + 240°
```

とする。

頂点座標は、

```text
x = cx + size * cos(theta)
y = cy - size * sin(theta)
```

とする。

rotation=0°では最初の頂点が右方向を向く。

---

## Square geometry

常に正方形とする。

外接円半径は `size`。

頂点角度は、

```text
rotation
rotation + 90°
rotation + 180°
rotation + 270°
```

とする。

頂点座標は三角形と同じ座標規約を使用する。

rotation=0°では最初の頂点が右方向を向く。

---

## Polygon rasterization

三角形・四角形について、subpixel centerがpolygon内部または境界上ならforegroundとする。

内部判定アルゴリズム自体は、同じ幾何結果を生成する限り実装側で選択可能とする。

---

## Foreground rendering

各sampleについて先にforeground RGBを決定する。

```text
inside subpixel:
  sample foreground RGB

outside subpixel:
  [0, 0, 0]
```

その後16 subpixelを平均してfinal pixel RGBを得る。

---

## Clipping

画像の連続幾何領域を、

```text
[-0.5, 63.5)
×
[-0.5, 63.5)
```

とする。

図形全体がこの領域内に存在しなければならない。

clippingは許可しない。

---

## Other constraints

- 背景を変動させない。
- runtime augmentationを使用しない。
- run開始後に画像生成条件を変更しない。

---

# DEC-B03 — Dataset Split

Status: APPROVED  
Source: review/BLOCKERS.md#B-03

各color × shape組み合わせ1,000件を独立に分割する。

---

## Split

```text
Train:      800 / combination
Validation: 100 / combination
Test:       100 / combination
```

全体:

```text
Train:      7200
Validation:  900
Test:        900
```

---

## Procedure

1. DEC-B02に従って全9,000 sampleを生成する。
2. 各sampleに一意な `sample_id` を付与する。
3. 各color × shapeグループ内で `split_seed` により決定的にshuffleする。
4. 先頭800件をTrainとする。
5. 次の100件をValidationとする。
6. 最後の100件をTestとする。
7. splitをmetadataへ固定保存する。

---

## Constraints

```text
Train ∩ Validation = ∅
Train ∩ Test = ∅
Validation ∩ Test = ∅
```

かつ、

```text
Train ∪ Validation ∪ Test
=
全9000 samples
```

でなければならない。

各splitには9種類すべてのcolor × shape組み合わせを含める。

Experiment 001では組み合わせhold-outを行わない。

---

## Usage

Train:

```text
Autoencoder training
probe training
Pixel baseline classifier training
```

Validation:

```text
Autoencoder validation loss measurement
probe C selection
Pixel baseline classifier C selection
```

Test:

```text
final evaluation only
```

Autoencoderのparameter updateまたはcheckpoint選択にValidation / Testを使用しない。

---

# DEC-B04 — Autoencoder Architecture

Status: APPROVED  
Source: review/BLOCKERS.md#B-04

Experiment 001のbaselineとしてConvolutional Autoencoderを使用する。

---

## Input

```text
shape: [3, 64, 64]
dtype: float32
range: [0.0, 1.0]
normalization: RGB / 255
```

---

## Encoder

```text
Conv2d:
  in: 3
  out: 32
  kernel: 4
  stride: 2
  padding: 1
  bias: true
ReLU

Conv2d:
  in: 32
  out: 64
  kernel: 4
  stride: 2
  padding: 1
  bias: true
ReLU

Conv2d:
  in: 64
  out: 128
  kernel: 4
  stride: 2
  padding: 1
  bias: true
ReLU

Conv2d:
  in: 128
  out: 256
  kernel: 4
  stride: 2
  padding: 1
  bias: true
ReLU

Flatten

Linear:
  in: 4096
  out: latent_dim
  bias: true
```

Encoder最終出力にはactivationを適用しない。

---

## Latent

```text
latent_dim: 32
activation: none
shape: [32]
```

正式baselineでは32を使用する。

実装上はconfigから変更可能としてよい。

---

## Decoder

```text
Linear:
  in: latent_dim
  out: 4096
  bias: true
ReLU

Reshape:
  [256, 4, 4]

ConvTranspose2d:
  in: 256
  out: 128
  kernel: 4
  stride: 2
  padding: 1
  bias: true
ReLU

ConvTranspose2d:
  in: 128
  out: 64
  kernel: 4
  stride: 2
  padding: 1
  bias: true
ReLU

ConvTranspose2d:
  in: 64
  out: 32
  kernel: 4
  stride: 2
  padding: 1
  bias: true
ReLU

ConvTranspose2d:
  in: 32
  out: 3
  kernel: 4
  stride: 2
  padding: 1
  bias: true
Sigmoid
```

---

## Weight initialization

ReLU直前の学習層には、

```text
Kaiming Uniform
mode: fan_in
nonlinearity: relu
```

を使用する。

対象:

```text
Encoder Conv2d layers

Decoder:
  Linear latent_dim → 4096
  ConvTranspose2d 256 → 128
  ConvTranspose2d 128 → 64
  ConvTranspose2d 64 → 32
```

Encoderのlatent出力LinearとDecoder最終ConvTranspose2dには、

```text
Xavier Uniform
gain: 1.0
```

を使用する。

---

## Bias initialization

全biasを、

```text
0.0
```

で初期化する。

---

## Initialization randomness

parameter initializationは `model_seed` のみに依存させる。

同一model seedから同一initial parameterを生成可能であること。

`initial.pt` はoptimizer update前に保存する。

---

## Numeric precision

```text
parameter_dtype: float32
activation_dtype: float32
loss_dtype: float32
```

---

## Mixed precision

```text
AMP: disabled
FP16: disabled
BF16: disabled
TF32: disabled
```

---

## Other constraints

以下は使用しない。

- Batch Normalization
- Dropout
- latent normalization

モデルの総parameter数を記録する。

architectureを結果確認後に変更し、同じbaselineとして扱ってはならない。

---

# DEC-B05 — Training Procedure

Status: APPROVED  
Source: review/BLOCKERS.md#B-05

Experiment 001 baselineの学習条件を以下とする。

---

## Objective

```text
image_reconstruction_only
```

---

## Loss

```text
Mean Squared Error
reduction: mean
```

---

## Optimizer

```text
Adam

learning_rate: 0.001
beta1: 0.9
beta2: 0.999
eps: 1e-8
weight_decay: 0
```

---

## Training

```text
epochs: 50
batch_size: 128
```

Train:

```text
shuffle: true
drop_last: false
seed: loader_seed
```

Validation:

```text
shuffle: false
drop_last: false
```

Test:

```text
shuffle: false
drop_last: false
```

---

## Disabled mechanisms

```text
learning_rate_scheduler: none
early_stopping: none
gradient_clipping: none
```

以下の正則化を使用しない。

- latent regularization
- sparsity penalty
- KL divergence
- contrastive loss

---

## Checkpoints

```text
initial.pt
final.pt
```

`initial.pt` は学習開始前。

`final.pt` は50 epoch終了後。

主解析対象は `final.pt`。

Validation lossによるbest checkpoint選択は行わない。

---

## Validation

各epoch終了後にValidation lossを測定する。

Validationは、

- Autoencoder parameter update
- early stopping
- checkpoint selection

には使用しない。

---

## Logging

最低限、

```text
epoch
training_loss
validation_loss
learning_rate
```

を記録する。

---

## Failure policy

学習失敗もrunとして保存する。

結果確認後に同一runの条件を書き換えない。

研究条件を変更する場合は、新しいDecisionと新しいrunとして扱う。

具体的なrun statusは `DEC-NB-v2-01` に従う。

---

# DEC-B06 — Linear Probe

Status: APPROVED  
Source: review/BLOCKERS.md#B-06

学習済み潜在表現からcolorおよびshapeがどの程度線形に読み出せるかを測定する。

---

## Encoder

```text
frozen: true
gradient_from_probe: prohibited
```

Train / Validation / Testすべてについて、initial / final Encoderのlatentを抽出する。

probe学習によるgradientをEncoderへ返してはならない。

---

## Latent standardization

probe入力前にlatentをTrain統計で標準化する。

```text
x' = (x - mean_train) / std_train
```

```text
ddof: 0
near_zero_std_threshold: 1e-8
near_zero_std_action: exclude_feature
```

initial Encoderについては、

```text
initial Train latent
```

のみからscalerをfitする。

final Encoderについては、

```text
final Train latent
```

のみからscalerをfitする。

initial / finalでscalerを共有しない。

Validation / Test統計をscaler fitに使用しない。

---

## Probes

color:

```text
multinomial logistic regression
classes:
  red
  green
  blue
```

shape:

```text
multinomial logistic regression
classes:
  circle
  triangle
  square
```

hidden layerは使用しない。

---

## Classifier configuration

```text
penalty: L2

C_candidates:
  - 0.01
  - 0.1
  - 1
  - 10
  - 100

fit_intercept: true
class_weight: none

solver: lbfgs
max_iter: 1000
tolerance: 1e-6
```

---

## Split usage

```text
Train:
  classifier training

Validation:
  C selection

Test:
  final evaluation only
```

---

## C selection

収束したcandidateのみを対象とする。

Validation accuracy最大のCを採用する。

同率の場合は最小Cを採用する。

---

## Non-convergence

非収束candidateはC選択対象から除外する。

すべてのC候補が非収束の場合、

```text
PROBE_FAILED
```

とする。

Experiment-levelの扱いは `DEC-NB-v2-01` に従う。

---

## Required metrics

```text
train_accuracy
train_balanced_accuracy

validation_accuracy
validation_balanced_accuracy

test_accuracy
test_balanced_accuracy

test_confusion_matrix
chance_level
selected_C
```

成功条件には通常の `test_accuracy` を使用する。

---

## Class order

color:

```text
red
green
blue
```

shape:

```text
circle
triangle
square
```

---

## Control consistency

initial / final Encoderで、

- preprocessing
- classifier
- C grid
- selection rule
- metrics

をすべて同一にする。

---

# DEC-B07 — Distance Analysis

Status: APPROVED  
Source: review/BLOCKERS.md#B-07

Test latent上で距離解析を行う。

---

## Pair selection

900 Test samplesについて全ユニークunordered pairを使用する。

```text
C(900,2) = 404550
```

自己pairを含めない。

順序違いの重複pairを含めない。

---

## Pair categories

```text
same_color_same_shape
same_color_different_shape
different_color_same_shape
different_color_different_shape
```

---

## Primary distance

Train latent統計によって標準化したEuclidean distanceを主解析とする。

```text
z' = (z - mean_train) / std_train
```

```text
ddof: 0
near_zero_std_threshold: 1e-8
near_zero_std_action: exclude_dimension
```

initial / finalそれぞれ自身のTrain latent統計を使用する。

---

## Secondary distance

```text
raw Euclidean
```

を補助解析として保存する。

---

## Aggregates

color:

```text
same_color
=
same_color_same_shape
+
same_color_different_shape
```

```text
different_color
=
different_color_same_shape
+
different_color_different_shape
```

shape:

```text
same_shape
=
same_color_same_shape
+
different_color_same_shape
```

```text
different_shape
=
same_color_different_shape
+
different_color_different_shape
```

`+` はpair集合の結合を意味する。

結合後の全pairから統計を再計算する。

---

## Statistics

各4カテゴリおよびaggregateについて最低限、

```text
count
mean_distance
median_distance
standard_deviation
bootstrap_95_percent_CI_for_mean
```

を保存する。

距離分布standard deviationも、

```text
ddof = 0
```

とする。

---

## Bootstrap

```text
iterations: 1000
resampling_unit: test_sample
sample_size_per_iteration: 900
replacement: true
seed: analysis_seed
```

---

## Bootstrap instance handling

復元抽出された各出現を別個のbootstrap instanceとして扱う。

各instanceには一意なbootstrap instance identityを持たせる。

同一original `sample_id` に由来するinstance同士のpairは除外する。

異なるoriginal sample_id間のpairについてはbootstrap multiplicityを反映して含める。

---

## Bootstrap pairing

各iterationでunique unordered instance pairsを構築する。

以下を除外する。

- 同一instanceのself-pair
- 同一original sample_id由来のinstance同士のpair

pairそのものを直接bootstrapしてはならない。

---

## Bootstrap distance source

保存済みTest latentを使用する。

standardized distanceでは承認済みTrain mean/stdを固定使用する。

bootstrap iterationごとにscalerをfitし直してはならない。

Encoderやprobeを再学習しない。

---

## Confidence interval

percentile bootstrapを使用する。

詳細なRNG・sampling・quantile規約は、

- `DEC-NB-v2-02`
- `DEC-NB-v3-01`

に従う。

---

# DEC-B08 — Pixel Baseline

Status: APPROVED  
Source: review/BLOCKERS.md#B-08

Pixel baselineを必須とする。

目的は、

> latentから読み出されたcolor/shape情報が、生画像の単純な統計または生pixel空間でも容易に読み出せる情報ではないか

を比較することである。

---

## Baseline 1 — Simple image statistics

使用features:

```text
mean_R
mean_G
mean_B
std_R
std_G
std_B
foreground_fraction
```

RGB統計のstandard deviationは、

```text
ddof = 0
```

とする。

foreground pixel:

```text
R + G + B > 0
```

を満たすpixel。

---

## Baseline 2 — Raw pixel linear

入力画像を `[0,1]` へ正規化する。

```text
3 × 64 × 64
→ flatten
→ 12288 features
```

---

## Feature standardization

両Pixel baselineについてTrain統計のみで標準化する。

```text
x' = (x - mean_train) / std_train
```

```text
ddof: 0
near_zero_std_threshold: 1e-8
near_zero_std_action: exclude_feature
```

Validation / Test統計をscaler fitに使用しない。

---

## Classifier

DEC-B06と完全に同じlogistic regression条件を使用する。

```text
multinomial logistic regression

penalty: L2

C:
  0.01
  0.1
  1
  10
  100

fit_intercept: true
class_weight: none

solver: lbfgs
max_iter: 1000
tolerance: 1e-6
```

---

## Split usage

```text
Train:
  classifier training

Validation:
  C selection

Test:
  final evaluation only
```

収束したcandidateのみを選択対象とする。

Validation accuracy最大を採用し、同率なら最小Cを採用する。

全候補非収束時は、

```text
PIXEL_BASELINE_FAILED
```

とする。

Experiment-levelの扱いは `DEC-NB-v2-01` に従う。

---

## Targets

```text
color
shape
```

を別々に評価する。

---

## Required metrics

```text
train_accuracy
train_balanced_accuracy

validation_accuracy
validation_balanced_accuracy

test_accuracy
test_balanced_accuracy

test_confusion_matrix
selected_C
chance_level
```

---

## Comparison conditions

以下は同じclassifier条件、C grid、選択規則、評価指標を使用する。

```text
initial Encoder latent probe
final Encoder latent probe
simple image statistics baseline
raw pixel linear baseline
```

入力featureのみが異なる。

---

## Interpretation constraints

- Pixel baselineをAutoencoder学習へ使用しない。
- Pixel baseline結果を見て同一runのAutoencoder条件を変更しない。
- latentがPixel baselineを上回ること自体を成功条件としない。
- Pixel baselineだけを根拠に概念核の有無を判断しない。

---

# DEC-NB-v2-01 — Run and Evaluation Failure Semantics

Status: APPROVED

Experiment 001では、runそのものの実行状態と、解析結果の完全性を分離して扱う。

---

## Run execution status

各正式runは、以下のいずれかの実行状態を持つ。

```text
VALID
INVALID
EXPERIMENTAL_FAILURE
```

### VALID

仕様どおり実行され、Autoencoder学習および必要な解析へ進めるrun。

### INVALID

技術的理由により科学的結果として使用できないrun。

例:

- 実装bug
- spec違反
- label leakage
- ファイル破損
- 実行中断
- hardware / environment障害
- VERIFY失敗

INVALID runは科学的な5-run集約へ含めない。

### EXPERIMENTAL_FAILURE

仕様どおり実行されたが、実験そのものが成立しなかったrun。

例:

- loss発散
- NaN
- Autoencoder学習失敗
- 学習結果により主要評価指標を取得できない

EXPERIMENTAL_FAILUREは削除せず、科学的結果として記録する。

---

## Evaluation flags

runには必要に応じて以下の解析flagを付与できる。

```text
PROBE_FAILED
DISTANCE_FAILED
BOOTSTRAP_CI_FAILED
PIXEL_BASELINE_FAILED
```

複数flagを同時に持つことを許可する。

---

## PROBE_FAILED

colorまたはshapeについて、SUCCESS判定に必要な正式probe指標を取得できない場合に付与する。

主要probe指標が取得できないため、完全なSUCCESS / NO_EVIDENCE判定はできない。

---

## DISTANCE_FAILED

distance contrastそのものを正常に計算できない場合に付与する。

主要距離指標が取得できないため、完全なSUCCESS / NO_EVIDENCE判定はできない。

---

## BOOTSTRAP_CI_FAILED

bootstrapの有効iteration数が950未満などの理由で95% CIを正常に算出できない場合に付与する。

Bootstrap CIはSUCCESS条件そのものには使用しない。

したがって、

```text
BOOTSTRAP_CI_FAILED
```

だけではSUCCESS / INCONCLUSIVE / NO_EVIDENCE判定を妨げない。

Experiment-level reportへ、

```text
DISTANCE_CI_INCOMPLETE
```

として明示する。

---

## PIXEL_BASELINE_FAILED

Pixel baseline classifierがすべて非収束するなどの理由でcontrol評価を完了できない場合に付与する。

Pixel baselineはSUCCESS条件には使用しない。

したがって、

```text
PIXEL_BASELINE_FAILED
```

だけではSUCCESS / INCONCLUSIVE / NO_EVIDENCE判定を妨げない。

Experiment-level reportへ、

```text
CONTROL_INCOMPLETE
```

として明示する。

---

## NOT_EVALUATED

正式5 master seedについて、

```text
同一git commit
AND
non-INVALID run
```

が5件すべて揃っていない場合、

```text
NOT_EVALUATED
```

とする。

NOT_EVALUATEDは科学的結論ではなく、Experiment-levelの管理状態である。

INVALID runが1件でも正式集合に残っている場合、SUCCESS / INCONCLUSIVE / NO_EVIDENCEを出してはならない。

---

## INCONCLUSIVE due to missing primary evidence

正式5 seedすべてについて同一commitのnon-INVALID runが存在するが、

- EXPERIMENTAL_FAILURE
- PROBE_FAILED
- DISTANCE_FAILED

のいずれかにより、SUCCESS判定に必要な5 seed分のprobeまたはdistance指標が完全に揃わない場合、

```text
INCONCLUSIVE
```

とする。

---

## SUCCESS / NO_EVIDENCE eligibility

SUCCESSまたはNO_EVIDENCEを判定できるのは、

```text
正式5 seedすべてがnon-INVALID

AND

5 seedすべてについて必要なprobe指標が存在

AND

5 seedすべてについて必要なdistance指標が存在
```

する場合のみとする。

BOOTSTRAP_CI_FAILEDおよびPIXEL_BASELINE_FAILEDのみでは、このeligibilityを失わない。

---

## Experiment-level aggregation precedence

Experiment-levelの状態判定は以下の順序で行う。

```text
1.
正式5 seedのnon-INVALID runが5件揃っているか

NO
-> NOT_EVALUATED

2.
SUCCESS判定に必要なprobe/distance指標が
5 seedすべてについて存在するか

NO
-> INCONCLUSIVE

3.
SUCCESS条件を満たすか

YES
-> SUCCESS

4.
事前定義されたINCONCLUSIVEの
正方向変化条件を満たすか

YES
-> INCONCLUSIVE

5.
それ以外

-> NO_EVIDENCE
```

`BOOTSTRAP_CI_FAILED` および `PIXEL_BASELINE_FAILED` は、この判定順序を変更しない。

---

# DEC-NB-v2-02 — Bootstrap Deterministic Numerical Convention

Status: APPROVED

Experiment 001のbootstrap解析について、同一入力・同一`analysis_seed`から同一結果を再現するため、乱数生成およびpercentile算出規約を固定する。

RNG APIおよびseed→index列の具体的規約については、後続の `DEC-NB-v3-01` を優先する。

---

## Random number generator

Bootstrap resamplingにはPCG64 familyを使用する。

具体的な実装APIは `DEC-NB-v3-01` で固定する。

---

## Bootstrap sampling

各iterationについて、Test sample indexを表す整数を900個独立に生成する。

```text
low: 0
high: 900
size: 900
replacement: true
```

すなわち、

```text
index ∈ {0,1,...,899}
```

から一様に900回復元抽出する。

Test sampleのindex順序は、解析入力として保存された決定的sample順序に対応させる。

---

## Bootstrap iterations

```text
iterations: 1000
```

とする。

RNG streamはiteration間で連続させる。

---

## Percentile CI

有効なbootstrap meanを昇順に並べ、

```text
y[0] <= y[1] <= ... <= y[n-1]
```

とする。

quantile `q` について、

```text
h = (n - 1) * q
i = floor(h)
f = h - i
```

を定義する。

`i < n - 1` の場合、

```text
Q(q)
=
(1 - f) * y[i]
+
f * y[i + 1]
```

とする。

`i = n - 1` の場合、

```text
Q(q) = y[n - 1]
```

とする。

これはlinear interpolationによるquantile定義である。

---

## 95% Confidence Interval

```text
lower = Q(0.025)
upper = Q(0.975)
```

とする。

---

## Missing iterations

対象カテゴリに有効pairが存在しないiterationはmissingとして除外する。

有効iteration数を `n` とする。

```text
n >= 950
```

の場合のみCIを有効とする。

```text
n < 950
```

の場合、

```text
BOOTSTRAP_CI_FAILED
```

とする。

---

# DEC-NB-v3-01 — Bootstrap RNG API Convention

Status: APPROVED

Experiment 001のbootstrap resamplingについて、同一`analysis_seed`から同一index列を一意に生成するため、乱数生成APIを固定する。

---

## RNG implementation

Bootstrap用RNGは、正式baselineにおいて以下を使用する。

```text
bit_generator:
  numpy.random.PCG64

generator:
  numpy.random.Generator
```

初期化は以下と同一でなければならない。

```python
rng = numpy.random.Generator(
    numpy.random.PCG64(analysis_seed)
)
```

`analysis_seed` はDEC-NB01で定義された32-bit unsigned integerをそのまま `numpy.random.PCG64` constructorへ渡す。

独自のseed展開処理を追加してはならない。

`numpy.random.default_rng()` には依存しない。

---

## Bootstrap index generation

各bootstrap iterationについて、index列は以下と同一の方法で生成する。

```python
indices = rng.integers(
    low=0,
    high=900,
    size=900,
    endpoint=False,
    dtype=numpy.int64,
)
```

各indexは、

```text
0 <= index < 900
```

を満たす。

独自のPCG64出力→range integer変換を実装してはならない。

---

## RNG stream

`rng` は1000 bootstrap iterationの開始前に一度だけ生成する。

1000 iteration全体で同一Generator instanceを連続使用する。

iterationごとに、

- 再seed
- Generator再生成
- PCG64再生成

を行ってはならない。

---

## Sampling order

iterationは、

```text
0
1
2
...
999
```

の順番で処理する。

各iterationで900 indexを一度だけ生成する。

概念的には、

```python
for iteration in range(1000):
    indices = rng.integers(
        low=0,
        high=900,
        size=900,
        endpoint=False,
        dtype=numpy.int64,
    )
```

と同一のindex列を生成すること。

---

## Test sample mapping

index `0...899` は、保存済みTest sampleの決定的順序へ対応する。

この順序はbootstrap開始前に固定し、iteration間で変更してはならない。

Test sample order自体もartifactとして再構成可能でなければならない。

---

## NumPy version

正式baselineの5 runは、同一NumPy versionを使用する。

実行時のNumPy versionをrun metadataおよびExperiment-level manifestへ記録する。

異なるNumPy versionのbootstrap結果を同一正式baseline集合へ混在させてはならない。

---

## Reproducibility requirement

以下が同一である場合、

```text
NumPy version
analysis_seed
Test sample order
Test latent
metadata
Train standardization statistics
```

bootstrap sample index列および最終CIが同一になることを要求する。

---

## Prohibited alternatives

正式baselineのbootstrap RNGには以下を使用しない。

- `numpy.random.default_rng()` によるbit generator default依存
- `numpy.random.RandomState`
- legacy global `numpy.random` state
- Python標準 `random`
- PyTorch RNG
- framework独自RNG
- 独自PCG64 integer mapping

---

# Global Decision Constraints

以下はExperiment 001全体に適用する。

## Research conditions

APPROVEDな研究条件をCodexが独自に変更してはならない。

曖昧な研究条件を発見した場合は実装を停止し、BLOCKERとして報告する。

---

## Label leakage

colorおよびshapeは、

- Autoencoder入力
- Autoencoder教師信号
- Autoencoder loss
- Autoencoder parameter update

に使用してはならない。

評価フェーズでのみ使用する。

---

## Failed runs

失敗したrun、INVALID run、EXPERIMENTAL_FAILURE runを削除してはならない。

既存runを上書きしてはならない。

---

## Post-hoc changes

結果確認後に、

- 成功条件
- dataset条件
- model architecture
- learning conditions
- primary analysis
- evaluation metric

を変更して、同一baseline実験として扱ってはならない。

変更が必要な場合は新しいDecisionと新しいrunまたは新しい実験として扱う。

---

## Interpretation

以下だけを根拠に概念核形成を断定してはならない。

- PCA
- probe accuracy
- latent distance
- Pixel baselineとの比較
- 単一seed
- 再構成画像

Experiment 001で認める結論は、

> 概念核候補となり得る再現可能な規則的潜在構造が形成されたか

までとする。
