# Experiment 001 実験仕様書

## 潜在空間における共通構造の形成

# 0. 概念核について

## 0.1 背景

人間は、異なる対象や状況の間に共通する概念を認識できる。

例えば「赤」という概念を考える。

人間は、

- 赤いリンゴ
- 赤い苺
- 赤い車
- 赤い光
- 赤い図形

など、互いに異なる対象について「赤」という共通性を認識できる。

本研究では、このような多数の異なる経験に共通し、別の状況でも再利用できる内部的な構造を仮に**「概念核」**と呼ぶ。

---

## 0.2 概念核と名称は同一ではない

概念核そのものと、人間がそれに付けた名称は区別する。

例えば、

```text
              日本語「赤」
                   ↑
英語 "red" ←【概念核 R】→ 視覚的な赤
                   ↓
              その他の表現
```

という関係を想定する。

したがって、

```text
概念核 R ≠ 「赤」という文字列
```

である。

「赤」という単語は、人間が概念を表現するために使用している記号の一つにすぎない。

本研究が最終的に形成したいのは単語そのものではなく、その背後に存在し得る共通構造である。

---

## 0.3 概念核は人間が直接定義しない

本研究では、

```text
red = 特定のベクトル
circle = 特定のベクトル
```

のように、人間が概念核を直接定義する方法を採用しない。

人間が概念核を決定すると、その人間の分類方法、文化、言語、先入観などがモデル内部の概念体系へ直接持ち込まれる可能性があるためである。

そのため、

> **概念核は観測された経験の中に存在する共通性から、モデル自身によって形成されるべきである。**

という立場を採用する。

---

## 0.4 AIにも概念の形を事前指定しない

Experiment 001では、概念核を、

- 一点
- ベクトル
- クラスタ
- 領域
- 方向
- 部分空間
- 曲面
- 状態変化
- 変換
- その他の構造

のいずれかであると事前には決定しない。

潜在表現自体が有限次元ベクトルで表現されることと、概念核候補そのものがベクトル一点であることは区別する。

---

## 0.5 概念核は固定された真理とは限らない

長期的には概念核を、

> **新しい経験によって生成・修正・分割・統合され得る内部仮説**

として扱う。

ただし、この修正能力そのものはExperiment 001の対象外とする。

---

## 0.6 本研究における暫定的な定義

> **概念核とは、多数の異なる経験に共通して現れ、それらを説明・区別・再構成し、未知の状況においても再利用できる可能性を持つ内部構造である。**

この定義は概念核の機能を定義するものであり、その物理的・数学的な形を定義するものではない。

---

## 0.7 「概念核候補」と「概念核」を区別する

以下の結果だけでは「概念核が形成された」と結論しない。

- PCA上でクラスタが形成された
- 同色画像の潜在距離が近かった
- 線形分類器が色を高精度で読み出せた

Experiment 001では、この段階の構造を**概念核候補**として扱う。

---

# 1. 目的

本研究の長期的な目的は、人間が概念を直接定義することなく、観測された経験から再利用可能な共通構造を自律的に形成するAIを構築することである。

Experiment 001では、

> **単純な視覚経験のみから学習したニューラルネットワーク内部に、人間が「色」「形」と呼ぶ性質に対応する共通構造が自発的に形成されるか**

を検証する。

本実験では概念核そのものの存在証明は行わない。

---

# 2. 仮説

単純図形を多数観測し、それらを圧縮・再構成するよう学習したニューラルネットワークでは、色・形ラベルを与えなくても、潜在空間に色や形に対応する規則的構造が形成される可能性がある。

その構造の形は事前に固定しない。

---

# 3. 正式Baseline Run集合

Experiment 001の正式baselineは、5つのmaster seedによる5 runで構成する。

## 3.1 Formal master seeds

```text
1001
1002
1003
1004
1005
```

この5 seedは実行前に固定し、結果確認後に変更してはならない。

---

## 3.2 Seed derivation

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

各runには、

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

## 3.3 5 runで変動させるもの

正式5 runでは、master seedから派生するすべての乱数系列を変化させる。

したがってrun間では、

- 画像生成
- dataset split
- model initialization
- DataLoader順序
- probe関連乱数
- analysis / bootstrap乱数

が変化する。

Experiment 001における再現性とは、

> **実験手続き全体を異なる乱数条件で繰り返しても、同様の構造形成傾向が観測されるか**

を意味する。

---

# 4. 人工世界

## 4.1 画像

```text
width: 64
height: 64
channels: RGB
background: [0, 0, 0]
```

保存時のRGB値は `0〜255` とし、モデル入力時には各channelを255で割って `[0.0, 1.0]` に正規化する。

---

## 4.2 色

```text
red:   [230, 25, 25]
green: [25, 230, 25]
blue:  [25, 25, 230]
```

各sampleについて、各RGB channelへ独立に、

```text
U_integer(-10, +10)
```

を加える。

foreground RGBは図形描画前にsample単位で一度だけ決定する。

最終RGB値は `[0,255]` に制限する。

---

## 4.3 形

以下の3種類を使用する。

- 円
- 正三角形
- 正方形

内部を単色で塗りつぶし、独立した輪郭線は使用しない。

---

## 4.4 組み合わせ

色3種類 × 形3種類の全9組み合わせを使用する。

Experiment 001では組み合わせhold-outを行わない。

---

# 5. 図形生成・Rasterization

## 5.1 Position

```text
center_x = U_integer(26, 38)
center_y = U_integer(26, 38)
```

---

## 5.2 Size

```text
definition: circumradius_px
size = U_integer(12, 16)
```

円ではradiusそのものを表す。

正三角形・正方形では外接円半径を表す。

---

## 5.3 Rotation

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

## 5.4 Coordinate system

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

## 5.5 Supersampling

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

---

## 5.6 Circle geometry

中心 `(cx,cy)`、radius=`size` とする。

subpixel `(px,py)` が、

```text
(px-cx)^2 + (py-cy)^2 <= size^2
```

なら内部とする。

境界上もinsideとする。

---

## 5.7 Triangle geometry

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

## 5.8 Square geometry

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

## 5.9 Polygon rasterization

三角形・四角形について、subpixel centerがpolygon内部または境界上ならforegroundとする。

内部判定アルゴリズム自体は、同じ幾何結果を生成する限り実装側で選択可能とする。

---

## 5.10 Foreground rendering

各sampleについて先にforeground RGBを決定する。

```text
inside subpixel:
  sample foreground RGB

outside subpixel:
  [0, 0, 0]
```

その後16 subpixelを平均してfinal pixel RGBを得る。

---

## 5.11 Clipping

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

## 5.12 その他の制約

- 背景を変動させない。
- runtime augmentationを使用しない。
- run開始後に画像生成条件を変更しない。

---

# 6. データセット

各color × shape組み合わせについて1,000 sampleを生成する。

```text
9 combinations × 1000 samples = 9000 samples
```

---

## 6.1 Split

各組み合わせを独立に、

```text
Train:      800 / combination
Validation: 100 / combination
Test:       100 / combination
```

へ分割する。

全体:

```text
Train:      7200
Validation:  900
Test:        900
```

---

## 6.2 Split procedure

1. 全9,000 sampleを生成する。
2. 各sampleに一意な `sample_id` を付与する。
3. 各color × shapeグループ内で `split_seed` により決定的にshuffleする。
4. 先頭800件をTrainとする。
5. 次の100件をValidationとする。
6. 最後の100件をTestとする。
7. splitをmetadataへ固定保存する。

---

## 6.3 Split constraints

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

---

## 6.4 Split usage

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
Pixel baseline C selection
```

Test:

```text
final evaluation only
```

Autoencoderのparameter updateまたはcheckpoint選択にValidation / Testを使用しない。

---

# 7. ラベルの扱い

生成プログラムは評価用metadataとして最低限、

```text
sample_id
split
color
shape
x
y
size
rotation
r
g
b
generation_seed
```

を保持する。

ただし、

**colorおよびshapeをAutoencoderの入力・教師信号・損失計算・parameter updateへ使用してはならない。**

Autoencoder学習経路から評価用metadataを分離する。

色・形ラベルは解析フェーズでのみ使用する。

---

# 8. モデル

Experiment 001ではConvolutional Autoencoderを使用する。

## 8.1 Input

```text
shape: [3, 64, 64]
dtype: float32
range: [0.0, 1.0]
normalization: RGB / 255
```

---

## 8.2 Encoder

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

## 8.3 Latent

```text
latent_dim: 32
activation: none
shape: [32]
```

正式baselineでは32を使用する。

実装上はconfigから変更可能としてよいが、別値を正式baselineとして使用してはならない。

---

## 8.4 Decoder

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

## 8.5 Weight initialization

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

## 8.6 Bias initialization

全biasを、

```text
0.0
```

で初期化する。

---

## 8.7 Initialization randomness

parameter initializationは `model_seed` のみに依存させる。

同一model seedから同一initial parameterを生成可能であること。

`initial.pt` はoptimizer update前に保存する。

---

## 8.8 Numeric precision

```text
parameter_dtype: float32
activation_dtype: float32
loss_dtype: float32

AMP: disabled
FP16: disabled
BF16: disabled
TF32: disabled
```

---

## 8.9 その他

以下は使用しない。

- Batch Normalization
- Dropout
- latent normalization

モデルの総parameter数を記録する。

architectureを結果確認後に変更し、同一baselineとして扱ってはならない。

---

# 9. 学習目的・損失関数

学習目的は画像再構成のみとする。

```text
loss:
  Mean Squared Error
  reduction: mean
```

以下は使用しない。

- 色・形を近付ける損失
- contrastive loss
- KL divergence
- sparsity penalty
- latent regularization

---

# 10. 学習手順

## 10.1 Optimizer

```text
Adam

learning_rate: 0.001
beta1: 0.9
beta2: 0.999
eps: 1e-8
weight_decay: 0
```

---

## 10.2 Training

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

## 10.3 Disabled mechanisms

```text
learning_rate_scheduler: none
early_stopping: none
gradient_clipping: none
```

---

## 10.4 Checkpoints

```text
initial.pt
final.pt
```

`initial.pt` は学習開始前。

`final.pt` は50 epoch終了後。

主解析対象は `final.pt` とする。

Validation lossによるbest checkpoint選択は行わない。

---

## 10.5 Validation

各epoch終了後にValidation lossを測定する。

Validationは、

- Autoencoder parameter update
- early stopping
- checkpoint selection

には使用しない。

---

## 10.6 Logging

最低限、

```text
epoch
training_loss
validation_loss
learning_rate
```

を記録する。

---

# 11. 潜在表現

`initial.pt` と `final.pt` の両方について、

- Train
- Validation
- Test

すべてのlatentを抽出・保存する。

最低限、

```text
encoder_state
split
sample_id
latent_0 ... latent_31
```

を一意に対応付けられること。

評価metadataと後から結合可能であること。

---

# 12. PCA

Test latentを2次元および3次元へ射影する。

色別・形別可視化では、同一Encoder状態について同一PCA射影座標を使用する。

`initial.pt` と `final.pt` の両方へ同一手順を適用する。

PCAは探索的可視化であり、成功判定には使用しない。

---

# 13. Linear Probe

## 13.1 Encoder

```text
frozen: true
gradient_from_probe: prohibited
```

probe学習によるgradientをEncoderへ返してはならない。

---

## 13.2 Latent standardization

probe入力前にlatentをTrain統計で標準化する。

```text
x' = (x - mean_train) / std_train
```

```text
ddof: 0
near_zero_std_threshold: 1e-8
near_zero_std_action: exclude_feature
```

initial Encoderについては `initial Train latent` だけからscalerをfitする。

final Encoderについては `final Train latent` だけからscalerをfitする。

initial / finalでscalerを共有しない。

Validation / Test統計をscaler fitに使用しない。

---

## 13.3 Classifier

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

## 13.4 Classifier configuration

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

## 13.5 Split usage

```text
Train:
  classifier training

Validation:
  C selection

Test:
  final evaluation only
```

---

## 13.6 C selection

収束したcandidateのみを対象とする。

Validation accuracy最大のCを採用する。

同率の場合は最小Cを採用する。

---

## 13.7 Non-convergence

非収束candidateは選択対象から除外する。

すべてのC候補が非収束の場合、

```text
probe_status: FAILED
reason: NO_CONVERGED_CANDIDATE
```

とする。

---

## 13.8 Required metrics

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

class order:

```text
color:
  red
  green
  blue

shape:
  circle
  triangle
  square
```

---

# 14. 距離解析

## 14.1 Pair selection

900 Test samplesについて全ユニークunordered pairを使用する。

```text
C(900,2) = 404550
```

自己pairを含めない。

順序違いの重複pairを含めない。

---

## 14.2 Pair categories

```text
same_color_same_shape
same_color_different_shape
different_color_same_shape
different_color_different_shape
```

---

## 14.3 Primary distance

Train latent統計によって標準化したEuclidean distanceを主解析とする。

```text
z' = (z - mean_train) / std_train
```

```text
ddof: 0
near_zero_std_threshold: 1e-8
near_zero_std_action: exclude_dimension
```

initial / finalはそれぞれ自身のTrain latent統計を使用する。

---

## 14.4 Secondary distance

```text
raw Euclidean
```

を補助解析として保存する。

---

## 14.5 Aggregates

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

## 14.6 Statistics

各4カテゴリおよびaggregateについて最低限、

```text
count
mean_distance
median_distance
standard_deviation
bootstrap_95_percent_CI_for_mean
```

を保存する。

距離分布のstandard deviationには、

```text
ddof = 0
```

を使用する。

---

# 15. Bootstrap

## 15.1 Basic configuration

```text
iterations: 1000
resampling_unit: test_sample
sample_size_per_iteration: 900
replacement: true
seed: analysis_seed
```

---

## 15.2 Bootstrap instance handling

復元抽出された各出現を別個のbootstrap instanceとして扱う。

同一original `sample_id` に由来するinstance同士のpairは除外する。

異なるoriginal sample間のpairについてはbootstrap multiplicityを反映して含める。

---

## 15.3 Bootstrap pairing

各iterationでunique unordered instance pairを構築する。

以下を除外する。

- 同一instanceのself-pair
- 同一original sample_id由来のinstance同士のpair

pairそのものを直接bootstrapしてはならない。

---

## 15.4 Distance source

保存済みTest latentを使用する。

standardized distanceでは承認済みTrain mean/stdを固定使用する。

bootstrap iterationごとにscalerをfitし直してはならない。

Encoderやprobeを再学習しない。

---

## 15.5 Confidence interval

```text
method: percentile
level: 0.95
lower_percentile: 2.5
upper_percentile: 97.5
```

---

## 15.6 Empty categories

あるiterationで対象カテゴリに有効pairが存在しない場合、そのiterationの対象統計をmissingとする。

CI計算ではmissing iterationを除外する。

最低有効iteration数:

```text
950
```

950未満の場合、

```text
bootstrap_status: FAILED
```

とする。

同一latent、metadata、analysis_seedから同一bootstrap結果を再現可能であること。

---
15.7 Bootstrap RNG

Bootstrap resamplingには PCG64 を使用する。

RNGは analysis_seed から一度だけ初期化する。

1000 iteration全体で1つの連続したrandom streamを使用し、iterationごとに再seedしてはならない。

各iterationではTest sample indexについて、

low: 0
high: 900
size: 900
replacement: true

として900件を復元抽出する。

Test sample indexは、解析入力として保存された決定的sample順序に対応する。

15.8 Bootstrap percentile convention

有効なbootstrap meanを昇順に、

y[0] <= y[1] <= ... <= y[n-1]

とする。

quantile q について、

h = (n - 1) * q
i = floor(h)
f = h - i

とする。

i < n - 1 の場合、

Q(q)
=
(1 - f) * y[i]
+
f * y[i + 1]

とする。

i = n - 1 の場合、

Q(q) = y[n - 1]

とする。

95% CIは、

lower = Q(0.025)
upper = Q(0.975)

とする。

有効iteration数が950未満の場合、

BOOTSTRAP_CI_FAILED

とする。

# 16. Pixel Baseline

Pixel baselineを必須とする。

## 16.1 Baseline 1 — Simple image statistics

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

RGB standard deviationは、

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

## 16.2 Baseline 2 — Raw pixel linear

入力画像を `[0,1]` に正規化する。

```text
3 × 64 × 64
→ flatten
→ 12288 features
```

---

## 16.3 Feature standardization

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

## 16.4 Classifier

Linear Probeと完全に同じlogistic regression条件を使用する。

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

## 16.5 Split usage

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

全候補非収束時はFAILEDとする。

---

## 16.6 Required metrics

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

## 16.7 Comparison conditions

以下は同じclassifier条件、C grid、選択規則、評価指標を使用する。

```text
initial Encoder latent probe
final Encoder latent probe
simple image statistics baseline
raw pixel linear baseline
```

入力featureのみが異なる。

Pixel baselineはAutoencoder学習へ使用しない。

latentがPixel baselineを上回ること自体を成功条件としない。

---

# 17. 成功条件

Experiment 001は概念核の存在を証明しない。

目的は、

> **再構成学習によって、学習前には弱かったcolorまたはshapeに対応する再現可能な規則的潜在構造が形成されたか**

を判定することである。

---

## 17.1 Probe delta

各attribute `A ∈ {color, shape}`について、

```text
probe_delta_A(seed)
=
final_encoder_test_accuracy_A(seed)
-
initial_encoder_test_accuracy_A(seed)
```

を定義する。

---

## 17.2 Probe success conditions

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

## 17.3 Distance contrast

color:

```text
distance_contrast_color
=
mean(different_color)
-
mean(same_color)
```

shape:

```text
distance_contrast_shape
=
mean(different_shape)
-
mean(same_shape)
```

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

## 17.4 Distance success conditions

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

## 17.5 SUCCESS

colorまたはshapeの少なくとも一方が、

- Probe success conditions
- Distance success conditions

の両方を満たす場合、

```text
SUCCESS
```

とする。

---

## 17.6 INCONCLUSIVE

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

また、正式5 runの中に `EXPERIMENTAL_FAILURE` が存在し、成功判定に必要な指標を完全に計算できない場合もINCONCLUSIVEとする。

---

## 17.7 NO_EVIDENCE

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

NO_EVIDENCEは概念核そのものが存在しないことを意味しない。

---

## 17.8 成功判定に使用しないもの

以下は単独では成功条件としない。

- PCAの見た目
- Pixel baselineとの大小関係
- 単一seedの高精度
- raw Euclidean distanceのみの差
- 再構成画像の見た目

SUCCESSでも「概念核を発見した」とは結論しない。

---

18. Run状態と評価状態

18.1 Run execution status

各正式runは、

VALID
INVALID
EXPERIMENTAL_FAILURE

のいずれかのexecution statusを持つ。

VALID

仕様どおり実行され、科学的解析へ使用可能なrun。

INVALID

技術的理由により科学的結果として使用できないrun。

例:

実装bug

spec違反

label leakage

ファイル破損

実行中断

hardware / environment障害

VERIFY失敗

INVALID runは削除しない。

EXPERIMENTAL_FAILURE

仕様どおり実行されたが、

loss発散

NaN

Autoencoder学習失敗

主要指標取得不能

など、実験そのものが成立しなかったrun。

EXPERIMENTAL_FAILUREも削除しない。

18.2 Evaluation flags

必要に応じて以下をrunへ記録する。

PROBE_FAILED
DISTANCE_FAILED
BOOTSTRAP_CI_FAILED
PIXEL_BASELINE_FAILED

複数flagを同時に持つことを許可する。

18.3 Probe failure

すべてのC候補が非収束するなどの理由によりSUCCESS判定に必要なprobe指標を取得できない場合、

PROBE_FAILED

とする。

この場合、正式5 runすべてが存在していても完全なSUCCESS / NO_EVIDENCE判定は行えない。

18.4 Distance failure

distance contrastそのものを計算できない場合、

DISTANCE_FAILED

とする。

この場合、完全なSUCCESS / NO_EVIDENCE判定は行えない。

18.5 Bootstrap CI failure

CIのみが算出不能の場合、

BOOTSTRAP_CI_FAILED

とする。

Bootstrap CIはSUCCESS条件ではないため、distance contrast本体が正常に存在する限り科学的三値判定は継続可能とする。

Experiment-level reportへ、

DISTANCE_CI_INCOMPLETE

を記録する。

18.6 Pixel baseline failure

Pixel baselineを完了できない場合、

PIXEL_BASELINE_FAILED

とする。

Pixel baselineはSUCCESS条件ではないため、科学的三値判定は継続可能とする。

Experiment-level reportへ、

CONTROL_INCOMPLETE

を記録する。

18.7 NOT_EVALUATED

正式5 master seedについて、

同一git commitのnon-INVALID run

が5件すべて揃っていない場合、

NOT_EVALUATED

とする。

NOT_EVALUATEDは科学的結論ではない。

18.8 INCONCLUSIVE due to missing primary evidence

正式5 seedすべてについて同一commitのnon-INVALID runが存在するが、

EXPERIMENTAL_FAILURE

PROBE_FAILED

DISTANCE_FAILED

のいずれかによりSUCCESS判定に必要な5 seed分の指標が完全に揃わない場合、

INCONCLUSIVE

とする。

18.9 Eligibility for SUCCESS / NO_EVIDENCE

SUCCESSまたはNO_EVIDENCEを判定できるのは、

formal run count = 5

AND

all 5 runs are non-INVALID

AND

all 5 runs contain required probe metrics

AND

all 5 runs contain required distance metrics

の場合のみとする。

以下だけではeligibilityを失わない。

BOOTSTRAP_CI_FAILED
PIXEL_BASELINE_FAILED

# 19. Run-levelとExperiment-level成果物

## 19.1 Run-level

個々のrunでは、

```text
SUCCESS
INCONCLUSIVE
NO_EVIDENCE
```

を判定しない。

最低限、

```text
OBSERVATIONS
METRICS
WARNINGS
ARTIFACTS
```

を記録する。

---

## 19.2 Experiment-level

正式5 runを集約したExperiment-level成果物でのみ、最終科学的判定を行う。

論理的には、

```text
runs/
  <individual runs>

aggregate/
  baseline_manifest
  aggregate_metrics
  report
```

を区別可能にする。

正確なファイル名や配置は実装側で決定してよい。

---

## 19.3 Baseline manifest

最低限、

```text
experiment_id
git_commit

formal_master_seeds:
  - 1001
  - 1002
  - 1003
  - 1004
  - 1005

各run:
  master_seed
  run_id
  derived seeds
  status
```

を保存する。

---

# 20. Run-level必須成果物

各runについて最低限以下を保存する。

## 20.1 実験設定

```text
experiment_id
run_id
git_commit

master_seed
generation_seed
split_seed
model_seed
loader_seed
probe_seed
analysis_seed

dataset configuration
model configuration
parameter count
training configuration
analysis configuration
```

---

## 20.2 Dataset metadata

全9,000 sampleについて最低限、

```text
sample_id
split
color
shape
x
y
size
rotation
r
g
b
generation_seed
```

を保存する。

---

## 20.3 Checkpoints

```text
initial.pt
final.pt
```

可能な限り、

```text
model_state_dict
optimizer_state_dict
epoch
training_loss
validation_loss
model_configuration
```

を含める。

---

## 20.4 Training log

```text
epoch
training_loss
validation_loss
learning_rate
```

を保存する。

---

## 20.5 Latent vectors

以下6状態を区別可能に保存する。

```text
initial × train
initial × validation
initial × test

final × train
final × validation
final × test
```

各latentは `sample_id` と対応可能であること。

---

## 20.6 PCA

initial / finalそれぞれについて、

- color表示
- shape表示

を保存する。

同一Encoder状態では色・形表示に同一PCA座標を使用する。

可能であればPCA座標とexplained varianceもmachine-readable形式で保存する。

---

## 20.7 Distance analysis

initial / finalそれぞれについて、

- standardized Euclidean
- raw Euclidean
- 4カテゴリ統計
- aggregate統計
- bootstrap CI
- Train mean/std
- 除外次元

を保存する。

---

## 20.8 Linear probe

initial / finalそれぞれについてcolor・shapeの、

```text
selected_C
train_accuracy
train_balanced_accuracy
validation_accuracy
validation_balanced_accuracy
test_accuracy
test_balanced_accuracy
test_confusion_matrix
chance_level
candidate convergence status
```

を保存する。

---

## 20.9 Pixel baseline

以下2種類についてcolor / shapeを評価し保存する。

```text
simple_image_statistics
raw_pixel_linear
```

---

## 20.10 Reconstruction quality

最低限、

- Train reconstruction loss
- Validation reconstruction loss
- Test reconstruction loss

を保存する。

さらに、固定された決定的方法で選ばれたsampleについて入力と再構成の比較画像を保存する。

再構成品質は成功条件には使用しない。

---

## 20.11 Run report

各runのreportには最低限、

1. 実験条件
2. 学習結果
3. 線形プローブ
4. 距離解析
5. Pixel baseline
6. PCA
7. OBSERVATIONS
8. METRICS
9. WARNINGS
10. ARTIFACTS

を記載する。

run単位で最終三値判定を行わない。

---

21.x Experiment-level aggregation precedence

Experiment-levelの状態判定は以下の順序で行う。

1. 正式5 seedのnon-INVALID runが5件揃っているか
   NO  -> NOT_EVALUATED

2. SUCCESS判定に必要なprobe/distance指標が
   5 seedすべてについて存在するか
   NO  -> INCONCLUSIVE

3. SUCCESS条件を満たすか
   YES -> SUCCESS

4. INCONCLUSIVEの正方向変化条件を満たすか
   YES -> INCONCLUSIVE

5. それ以外
   -> NO_EVIDENCE

BOOTSTRAP_CI_FAILED および PIXEL_BASELINE_FAILED は、この判定順序を変更しない。

ただしreportに該当する不完全性を明示する。

# 22. 再現性

すべてのrunについて、

```text
experiment_id
run_id
git_commit
全seed
dataset_config
model_config
training_config
analysis_config
results
```

を記録する。

同じcommit、設定、seedから、

- dataset
- split
- initial parameter
- DataLoader順序
- probe設定
- bootstrap結果

を可能な限り再現できること。

同一environment + 同一commit + 同一seedでの再現を主要要件とする。

異なるhardware間でのbitwise完全一致までは要求しない。

---

# 23. Experiment 001では行わないこと

以下は後続実験に回す。

- 言語
- Transformer / LLM
- 実写画像
- 概念核の明示的生成
- 概念核の統合
- 概念核の分割
- 誤認からの修正
- 継続学習
- 未知概念の発見
- 未知の色×形組み合わせへの一般化評価
- 人間との会話
- 現実課題の解決

Experiment 001では、

> **共通構造が自然に形成されるか**

のみを扱う。

---

# 24. 研究上の原則

本実験では以下を守る。

**・概念をモデルに直接教えない。**

**・概念核の形を事前に決めない。**

**・可視化だけを根拠に概念の存在を断定しない。**

**・評価用ラベルと学習用情報を明確に分離する。**

**・仮説に反する結果も保存する。**

**・失敗runを削除しない。**

**・再現可能性を重視する。**

**・結果確認後に成功条件を変更しない。**

**・承認済み研究条件を実装側で暗黙に変更しない。**

**・曖昧な研究条件が見つかった場合は実装を停止し、BLOCKERとして報告する。**

---

# Experiment 001の問い

> **人間が「赤」「青」「円」「四角」といった概念を教師として与えなくても、単純な視覚経験を再構成する過程で、それらに対応する共通構造はAI内部に自発的に形成されるのか？**
