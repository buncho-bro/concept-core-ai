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

# 3. 人工世界

## 3.1 画像

```text
width: 64 px
height: 64 px
channels: RGB
background: (0, 0, 0)
```

画像内には単一の図形を配置する。

保存時のRGB値は `0〜255` とし、モデル入力時には各channelを255で割り `[0.0, 1.0]` に正規化する。

---

## 3.2 色

```text
red   = (230, 25, 25)
green = (25, 230, 25)
blue  = (25, 25, 230)
```

各RGB channelへ独立に、

```text
U_integer(-10, +10)
```

の変動を加える。

最終RGB値は `[0,255]` に収める。

承認済み基準値と変動幅では通常clipは発生しないが、安全のため範囲制約を設ける。

---

## 3.3 形

使用する図形は、

- 円
- 三角形
- 四角形

とする。

内部を単色で塗りつぶし、独立した輪郭線は使用しない。

---

## 3.4 組み合わせ

色3種類 × 形3種類の全9組み合わせを生成する。

Experiment 001では組み合わせhold-outを行わない。

---

# 4. 変動要素

## 4.1 位置

```text
center_x = U_integer(26, 38)
center_y = U_integer(26, 38)
```

---

## 4.2 大きさ

`size` は図形の外接円半径をpixel単位で表した値とする。

```text
size = U_integer(12, 16)
```

円では半径そのものとする。

---

## 4.3 回転

```text
circle:
  rotation = 0

triangle:
  rotation = U(0, 360) degrees

square:
  rotation = U(0, 360) degrees
```

---

## 4.4 描画

4倍supersamplingを使用する。

```text
internal_resolution = 256 × 256
final_resolution = 64 × 64
supersampling_factor = 4
```

すべての図形で同一の描画・縮小方式を使用する。

---

## 4.5 制約

- 図形全体が画像内に収まること。
- clippingを許可しない。
- 背景を変動させない。
- 実行時augmentationを使用しない。
- run開始後に画像生成条件を変更しない。

---

# 5. データセット

各色×形の組み合わせについて1,000画像を生成する。

```text
9 combinations × 1000 samples = 9000 samples
```

## 5.1 分割

各組み合わせを独立に、

```text
Train      800
Validation 100
Test       100
```

へ分割する。

全体では、

```text
Train      7200
Validation  900
Test        900
```

となる。

---

## 5.2 分割手順

1. 全9,000サンプルを生成する。
2. 各サンプルへ一意な `sample_id` を付与する。
3. 色×形ごとのグループ内で `split_seed` により決定的にshuffleする。
4. 先頭800件をTrain、次の100件をValidation、最後の100件をTestとする。
5. split結果をmetadataへ保存する。

---

## 5.3 制約

```text
Train ∩ Validation = ∅
Train ∩ Test = ∅
Validation ∩ Test = ∅
```

かつ、

```text
Train ∪ Validation ∪ Test = 全9000サンプル
```

でなければならない。

`split_seed` は画像生成用乱数から独立させる。

---

# 6. ラベルの扱い

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

**colorおよびshapeをAutoencoderの入力・教師信号・損失計算へ使用してはならない。**

Autoencoder学習経路から評価用metadataを分離する。

色・形ラベルはAutoencoder学習終了後の解析にのみ使用する。

---

# 7. モデル

Experiment 001ではConvolutional Autoencoderを使用する。

## 7.1 Encoder

```text
Input: 3 × 64 × 64

Conv2d 3 → 32
kernel=4 stride=2 padding=1
ReLU

Conv2d 32 → 64
kernel=4 stride=2 padding=1
ReLU

Conv2d 64 → 128
kernel=4 stride=2 padding=1
ReLU

Conv2d 128 → 256
kernel=4 stride=2 padding=1
ReLU

Flatten

Linear 4096 → latent_dim
```

Encoder最終出力にはactivationを適用しない。

---

## 7.2 Decoder

```text
Linear latent_dim → 4096
ReLU

Reshape → 256 × 4 × 4

ConvTranspose2d 256 → 128
kernel=4 stride=2 padding=1
ReLU

ConvTranspose2d 128 → 64
kernel=4 stride=2 padding=1
ReLU

ConvTranspose2d 64 → 32
kernel=4 stride=2 padding=1
ReLU

ConvTranspose2d 32 → 3
kernel=4 stride=2 padding=1
Sigmoid
```

---

## 7.3 その他

以下は使用しない。

- Batch Normalization
- Dropout
- latent normalization

モデルの総parameter数を記録する。

---

# 8. 潜在空間

正式baselineでは、

```text
latent_dim = 32
```

とする。

実装上はconfigから変更可能とするが、baseline runでは32を使用する。

潜在表現が32次元ベクトルであることは、概念核候補そのものが単一ベクトルであることを意味しない。

---

# 9. 損失関数

学習目的は画像再構成のみとする。

```text
loss = Mean Squared Error
reduction = mean
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
optimizer = Adam
learning_rate = 0.001
beta1 = 0.9
beta2 = 0.999
eps = 1e-8
weight_decay = 0
```

learning rate schedulerは使用しない。

---

## 10.2 学習条件

```text
epochs = 50
batch_size = 128
```

```text
Train:
  shuffle = true
  drop_last = false

Validation:
  shuffle = false
  drop_last = false

Test:
  shuffle = false
  drop_last = false
```

Train DataLoaderには `loader_seed` を使用する。

early stoppingおよびgradient clippingは使用しない。

---

## 10.3 Checkpoint

最低限、

```text
initial.pt
final.pt
```

を保存する。

`initial.pt` は学習開始前、`final.pt` は50 epoch終了後とする。

主解析対象は `final.pt` とする。

Validation lossによるbest checkpoint選択は行わない。

---

## 10.4 Validation

各epoch終了後にValidation lossを測定する。

Validationは、

- parameter更新
- early stopping
- baseline checkpoint選択

には使用しない。

---

## 10.5 失敗run

失敗runも保存する。

条件変更が必要な場合は同一runを書き換えず、新しいDecisionおよび新しいrunとして扱う。

---

# 11. 潜在表現の保存

`initial.pt` と `final.pt` の両方について、

- Train
- Validation
- Test

の潜在表現を保存する。

保存形式は実装側で決定してよいが、少なくとも、

```text
encoder_state
split
sample_id
latent_0 ... latent_31
```

を一意に対応付けられること。

解析時には評価用metadataと結合可能であること。

---

# 12. 解析

## 12.1 PCA

Test latentを2次元および3次元へ射影する。

色別・形別可視化では同一PCA射影座標を使用する。

`initial.pt` と `final.pt` の両方に同一手順を適用する。

PCAは探索的可視化であり、成功判定には使用しない。

---

## 12.2 線形プローブ

Encoderを固定し、latentのみからcolorおよびshapeを予測する。

```text
color probe:
  latent → multinomial logistic regression → 3 classes

shape probe:
  latent → multinomial logistic regression → 3 classes
```

hidden layerは使用しない。

### split

```text
Train:
  probe training

Validation:
  regularization selection

Test:
  final evaluation
```

### 正則化

L2正則化を使用する。

```text
C ∈ {0.01, 0.1, 1, 10, 100}
```

Validation accuracy最大のCを採用する。

同率の場合は最小Cを採用する。

### 指標

最低限、

```text
train_accuracy
validation_accuracy
test_accuracy
balanced_accuracy
confusion_matrix
chance_level
```

を保存する。

chance levelはcolor、shapeともに `1/3` とする。

`initial.pt` と `final.pt` に同じprobe手順を適用する。

probeからEncoderへ勾配を返してはならない。

---

## 12.3 距離解析

Test splitの全ユニークペアを使用する。

Testが900サンプルの場合、

```text
C(900,2) = 404550 pairs
```

となる。

自己ペアおよび順序違いの重複ペアを含めない。

ペアを以下へ分類する。

```text
same_color_same_shape
same_color_different_shape
different_color_same_shape
different_color_different_shape
```

### 主距離

Train latent統計で各次元を標準化したEuclidean距離を使用する。

```text
z' = (z - mean_train) / std_train
```

`std < 1e-8` の次元は除外する。

`initial.pt` と `final.pt` はそれぞれ自身のTrain latent統計を使用する。

### 補助距離

raw Euclidean distanceも保存する。

---

## 12.4 距離aggregateの定義

colorについて、

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

とする。

shapeについて、

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

とする。

ここで `+` はペア集合の結合を意味し、各集合を結合した全ペアから距離統計を再計算する。

---

## 12.5 距離統計

各4カテゴリおよびaggregateについて最低限、

```text
count
mean_distance
median_distance
standard_deviation
bootstrap_95_percent_CI_for_mean
```

を保存する。

Bootstrapは、

```text
iterations = 1000
resampling_unit = test_sample
```

とし、`analysis_seed` を使用する。

距離pair自体を独立サンプルとして直接bootstrapしてはならない。

---

# 13. コントロール

## 13.1 未学習Encoder

`initial.pt` に対して、

- PCA
- 距離解析
- 線形プローブ

を`final.pt`と同じ方法で実施する。

---

## 13.2 Pixel baseline

Pixel baselineは必須とする。

### Simple image statistics baseline

```text
mean_R
mean_G
mean_B
std_R
std_G
std_B
foreground_fraction
```

を使用する。

`foreground_fraction` は、

```text
R + G + B > 0
```

を満たすpixelの割合とする。

### Raw pixel linear baseline

画像を `[0,1]` に正規化し、

```text
3 × 64 × 64
→ flatten
→ 12288 dimensions
```

として線形分類器へ入力する。

### 標準化

Train統計のみを使用する。

```text
x' = (x - mean_train) / std_train
```

`std < 1e-8` のfeatureは除外する。

### 分類

multinomial logistic regressionを使用する。

```text
C ∈ {0.01, 0.1, 1, 10, 100}
```

Trainで学習、ValidationでCを選択し、Testで最終評価する。

colorとshapeを別々に評価する。

Pixel baselineは結果解釈用controlであり、Autoencoderの学習条件へ影響させてはならない。

---

# 14. 成功条件

Experiment 001は概念核の存在を証明しない。

成功判定は、

> **再構成学習によって、学習前には弱かったcolorまたはshapeに対応する再現可能な規則的潜在構造が形成されたか**

を評価するために行う。

正式baselineは5 seedで実施する。

---

## 14.1 主判定：線形プローブ

属性 `A ∈ {color, shape}` について、

```text
probe_delta_A
=
final_encoder_test_accuracy
-
initial_encoder_test_accuracy
```

を定義する。

以下をすべて満たすこと。

1. 5 seed中4 seed以上で `probe_delta_A > 0`
2. 5 seedの `probe_delta_A` 中央値が `>= 0.10`
3. final Encoder Test accuracyの5 seed中央値が `>= 0.70`

---

## 14.2 確認判定：距離解析

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

とする。

主距離であるstandardized Euclideanを使用する。

同じ属性について、

1. final Encoderで5 seed中4 seed以上 `distance_contrast_A > 0`
2. 5 seed中央値で `distance_contrast_final > distance_contrast_initial`

を満たすこと。

---

## 14.3 Experiment判定

### SUCCESS

colorまたはshapeの少なくとも一方が、

- 線形プローブ条件
- 距離解析条件

の両方を満たす。

### INCONCLUSIVE

規則性または改善は観測されたが、事前に定めた成功条件を完全には満たさない。

### NO_EVIDENCE

color・shapeとも成功条件を満たさず、学習による一貫した構造強化を確認できない。

---

## 14.4 成功判定に使用しないもの

以下は単独では成功条件としない。

- PCAの見た目
- Pixel baselineとの大小関係
- 単一seedでの高精度
- raw Euclidean distanceのみの差
- 再構成画像の見た目

SUCCESSでも「概念核を発見した」とは結論しない。

---

# 15. 失敗も結果として扱う

以下も正式な結果として保存する。

- colorのみ成功条件を満たす
- shapeのみ成功条件を満たす
- 両方が成功条件を満たす
- INCONCLUSIVE
- NO_EVIDENCE
- seedによる大きな変動
- 再構成は成功したが潜在構造が形成されない
- 学習そのものが失敗する

結果確認後に基準を変更して成功扱いしてはならない。

---

# 16. Experiment 001では行わないこと

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

# 17. 再現性

すべてのrunについて最低限、

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

dataset_config
model_config
training_config
analysis_config
results
```

を記録する。

用途別seedはmaster seedから決定的に導出するか、独立値として明示的に保存する。

同じ設定とseedから同じデータセット・splitを再生成できること。

run開始時の研究条件を固定し、途中で変更しない。

失敗runも削除しない。

---

# 18. Experiment 001の最終成果物

1回のrunごとに独立して保存する。

成果物の正確なディレクトリ構成やファイル分割方法は実装側で決定してよい。

ただし、以下を一意に区別・再解析できる状態で保存しなければならない。

## 18.1 実験設定

最低限、

```text
experiment_id
run_id
git_commit

全seed
dataset configuration
model configuration
parameter count
training configuration
analysis configuration
```

を保存する。

---

## 18.2 Dataset metadata

全9,000サンプルについて最低限、

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

## 18.3 Checkpoint

最低限、

```text
initial.pt
final.pt
```

を保存する。

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

## 18.4 Training log

1 epochにつき1行として最低限、

```text
epoch
training_loss
validation_loss
learning_rate
```

を保存する。

---

## 18.5 Latent vectors

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

## 18.6 PCA

initial / finalそれぞれについて、

- color表示
- shape表示

を保存する。

同一Encoder状態では色・形表示に同一PCA座標を使用する。

可能であればPCA座標とexplained varianceもmachine-readable形式で保存する。

---

## 18.7 距離解析

initial / finalそれぞれについて、

- standardized Euclidean
- raw Euclidean

の結果を保存する。

標準化に使用したTrain mean/stdと除外次元も保存する。

---

## 18.8 Linear probe

initial / finalそれぞれについてcolor・shapeの、

```text
selected_C
train_accuracy
validation_accuracy
test_accuracy
balanced_accuracy
confusion_matrix
chance_level
```

を保存する。

候補CごとのValidation結果も保存する。

---

## 18.9 Pixel baseline

以下2種類を保存する。

```text
simple_image_statistics
raw_pixel_linear
```

color / shapeをそれぞれ評価する。

---

## 18.10 再構成品質

最低限、

- Train reconstruction loss
- Validation reconstruction loss
- Test reconstruction loss

を保存する。

さらに、固定された決定的方法で選ばれたsampleについて入力と再構成の比較画像を保存する。

再構成品質はExperiment 001の成功条件には使用しない。

---

## 18.11 Report

`report.md` には最低限、

1. 実験条件
2. 学習結果
3. 線形プローブ
4. 距離解析
5. Pixel baseline
6. PCA
7. 成功条件判定
8. 観測
9. 解釈
10. 限界
11. 次の実験への示唆

を記載する。

観測と解釈を分離する。

最終判定は、

```text
SUCCESS
INCONCLUSIVE
NO_EVIDENCE
```

のいずれかとして記録する。

---

# 19. 研究上の原則

本実験では以下を守る。

**・概念をモデルに直接教えない。**

**・概念核の形を事前に決めない。**

**・可視化だけを根拠に概念の存在を断定しない。**

**・評価用ラベルと学習用情報を明確に分離する。**

**・仮説に反する結果も保存する。**

**・再現可能性を重視する。**

**・結果確認後に成功条件を変更しない。**

---

## Experiment 001の問い

> **人間が「赤」「青」「円」「四角」といった概念を教師として与えなくても、単純な視覚経験を再構成する過程で、それらに対応する共通構造はAI内部に自発的に形成されるのか？**
