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

さらに、

```text id="m8r23s"
リンゴの赤
     │
苺の赤
     │
車の赤
     │
光の赤
     │
未知の物体の赤
```

のように、対象そのものが未知であっても「赤」という性質を再利用して理解することができる。

本研究では、このような多数の異なる経験に共通し、別の状況でも再利用できる内部的な構造を仮に**「概念核」**と呼ぶ。

---

## 0.2 概念核と名称は同一ではない

概念核そのものと、人間がそれに付けた名称は区別する。

例えば、

```text id="u45hbr"
              日本語「赤」
                   ↑
英語 "red" ←【概念核 R】→ 視覚的な赤
                   ↓
              その他の表現
```

という関係を想定する。

したがって、

```text id="w2d54u"
概念核 R ≠ 「赤」という文字列
```

である。

「赤」という単語は、人間が概念を表現するために使用している記号の一つにすぎない。

本研究が最終的に形成したいのは単語そのものではなく、その背後に存在し得る共通構造である。

---

## 0.3 概念核は人間が直接定義しない

本研究では、

```text id="z5z0w5"
red = 特定のベクトル
circle = 特定のベクトル
```

のように、人間が概念核を直接定義する方法を採用しない。

人間が概念核を決定すると、その人間の分類方法、文化、言語、先入観などがモデル内部の概念体系へ直接持ち込まれる可能性があるためである。

そのため、

> **概念核は観測された経験の中に存在する共通性から、モデル自身によって形成されるべきである。**

という立場を本研究では採用する。

---

## 0.4 AIにも概念の形を事前指定しない

一方で、AIに完全に自由な概念体系を形成させる場合、人間の概念体系とは大きく異なる内部構造が形成される可能性がある。

これは将来的に人間とAIを接続する際の問題となり得る。

しかしExperiment 001では、この問題を解決しようとはしない。

まず、

> **観測経験だけから何らかの再利用可能な共通構造が形成されるのか**

を調べる。

そのため、概念核を、

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

例えば、

```text id="umhhdp"
丸 ─────────→ 赤い丸
四角 ───────→ 赤い四角
三角 ───────→ 赤い三角
        ↑
    共通する変化 R
```

という構造が形成された場合、「赤」に対応する概念核候補は一点ではなく、潜在表現を変化させる共通の**方向または変換**として存在している可能性もある。

---

## 0.5 概念核は固定された真理とは限らない

本研究では、形成された概念核が常に正しいとは仮定しない。

限られた経験しか存在しない場合、AIが異なる概念を同一のものとして扱う可能性がある。

例えば、

```text id="v8r6di"
経験：

赤い丸
赤い丸
赤い丸

        ↓

誤った内部構造：

「赤」 ≒ 「丸」
```

となる可能性がある。

その後、

```text id="ic5smh"
赤い四角
青い丸
赤い三角
```

などの反例を経験することで、

```text id="07evrx"
「赤」
  と
「丸」

は独立した構造なのではないか
```

と内部表現が再構成されることが望ましい。

したがって長期的には概念核を、

> **新しい経験によって生成・修正・分割・統合され得る内部仮説**

として扱う。

ただし、この修正能力そのものはExperiment 001の対象外とする。

---

## 0.6 本研究における暫定的な定義

以上を踏まえ、本研究では「概念核」を暫定的に以下のように定義する。

> **概念核とは、多数の異なる経験に共通して現れ、それらを説明・区別・再構成し、未知の状況においても再利用できる可能性を持つ内部構造である。**

この定義は概念核の**機能**を定義するものであり、その物理的・数学的な形を定義するものではない。

概念核が実際に、

```text id="bl1zm4"
点なのか
方向なのか
領域なのか
変換なのか
複数構造の組み合わせなのか
```

については実験結果から検討する。

---

## 0.7 「概念核候補」と「概念核」を区別する

本研究では、ニューラルネットワーク内部に何らかの規則的構造を発見しただけでは、それを概念核とは呼ばない。

例えば、

- PCA上でクラスタが形成された
- 同色画像の潜在距離が近かった
- 線形分類器が色を高精度で読み出せた

という結果だけでは、

> 「赤という概念核が形成された」

とは結論しない。

この段階では**「概念核候補」**と呼ぶ。

概念核と呼ぶためには、後続実験において少なくとも、

```text id="8ekzlx"
異なる状況で共通して利用できる

        ＋

未知の状況でも再利用できる

        ＋

単なる入力統計では説明しにくい
```

といった性質を検証する必要がある。

Experiment 001では、その前段階として**概念核候補となり得る内部構造が自然に形成されるか**を調べる。

---

# 1. 目的

本研究の長期的な目的は、人間が概念を直接定義することなく、観測された経験から再利用可能な共通構造を自律的に形成するAIを構築することである。

Experiment 001では、その最も基本的な問いを検証する。

**研究質問：**

> 単純な視覚経験のみから学習したニューラルネットワーク内部に、人間が「色」「形」と呼ぶ性質に対応する共通構造が自発的に形成されるか？

本実験では「概念核」の存在を証明することを目的としない。

まず、概念核候補となり得る潜在構造が形成されるかを観測する。

---

## 2. 仮説

単純図形を多数観測し、それらを圧縮・再構成するよう学習したニューラルネットワークでは、学習時に色・形ラベルを与えなくても、潜在空間に色や形に対応する何らかの規則的構造が形成される可能性がある。

ただし、その構造が以下のどれになるかは事前に決めない。

- 点
- クラスタ
- 方向
- 領域
- 部分空間
- 曲面
- 変換
- その他の構造

「概念核はこの形である」という前提をモデルに与えない。

---

3. 人工世界

3.1 画像

画像は以下の条件とする。

width: 64 px
height: 64 px
channels: RGB
background: (0, 0, 0)

画像内には単一の図形のみを配置する。

入力画像は保存時にはRGB値 0〜255 を使用し、モデル入力時には各channelを255で割って [0.0, 1.0] へ正規化する。

3.2 色

3種類を使用する。

red   = (230, 25, 25)
green = (25, 230, 25)
blue  = (25, 25, 230)

各画像について、各RGB channelへ独立に

U_integer(-10, +10)

の変動を加える。

RGB値は有効範囲 [0,255] に収める。

3.3 形

3種類を使用する。

円

三角形

四角形

各図形は内部を単色で塗りつぶし、独立した輪郭線は使用しない。

3.4 組み合わせ

色3種類 × 形3種類の全組み合わせを生成する。

合計9種類の基本組み合わせとする。

Experiment 001では組み合わせhold-outを行わず、9種類すべてをTrain / Validation / Testに含める。

4. 変動要素

同じ色・形の組み合わせでも画像ごとに状態を変化させる。

4.1 位置

図形中心座標を以下から独立に一様抽出する。

center_x = U_integer(26, 38)
center_y = U_integer(26, 38)

4.2 大きさ

size は図形の外接円半径（circumradius）をpixel単位で表した値と定義する。

size = U_integer(12, 16)

円では半径そのものを表す。

三角形・四角形では、全頂点が接する外接円の半径を表す。

4.3 回転

circle:
  rotation = 0

triangle:
  rotation = U(0, 360) degrees

square:
  rotation = U(0, 360) degrees

4.4 描画

図形境界の描画差を抑えるため、4倍supersamplingを使用する。

internal_resolution = 256 × 256
final_resolution = 64 × 64
supersampling_factor = 4

すべての図形に同一の描画・縮小方式を使用する。

4.5 制約

図形全体が画像内に収まること。

clippingを許可しない。

背景は変動させない。

実行時augmentationを使用しない。

画像生成条件はrun開始後に変更しない。

5. データセット

各色×形の組み合わせについて1,000画像を生成する。

9 combinations × 1000 samples = 9000 samples

5.1 分割

各組み合わせを独立に以下へ分割する。

Train      800
Validation 100
Test       100

したがって全体は、

Train      7200
Validation  900
Test        900

となる。

5.2 分割手順

全9,000サンプルを生成する。

各サンプルへ一意な sample_id を付与する。

各色×形グループ内で split_seed を使用して決定的にshuffleする。

先頭800件をTrain、次の100件をValidation、最後の100件をTestとする。

決定したsplitを dataset_metadata.csv に保存する。

5.3 制約

Train ∩ Validation = ∅
Train ∩ Test = ∅
Validation ∩ Test = ∅

かつ、

Train ∪ Validation ∪ Test = 全9000サンプル

でなければならない。

split_seed は画像生成用乱数とは独立させる。

6. ラベルの扱い

生成プログラムは評価用metadataとして最低限、

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

を保持する。

ただし、

colorおよびshapeをAutoencoderの入力・教師信号・損失計算へ使用してはならない。

Autoencoder学習用Dataset/DataLoaderから評価metadataへ直接到達できない実装とする。

色・形ラベルはAutoencoder学習終了後の解析にのみ使用する。

7. モデル

Experiment 001ではConvolutional Autoencoderを使用する。

7.1 Encoder

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

Encoder最終出力にはactivationを適用しない。

7.2 Decoder

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

7.3 その他

以下は使用しない。

Batch Normalization

Dropout

latent normalization

モデルの総parameter数を各runで記録する。

8. 潜在空間

Experiment 001 baselineでは、

latent_dim = 32

を使用する。

実装上はconfigから変更可能とするが、正式baseline runでは32を使用する。

潜在表現は32次元実数ベクトルとして出力されるが、これは概念核そのものを32次元ベクトル一点と仮定することを意味しない。

潜在空間内に形成される、

クラスタ

領域

方向

部分空間

変換に対応する関係

その他の構造

を観測対象とする。

9. 損失関数

Autoencoderの学習目的は画像再構成のみとする。

loss = Mean Squared Error
reduction = mean

RGB全channel・全pixel・全batchについて平均する。

以下の損失または正則化は使用しない。

色を近付ける損失

形を近付ける損失

contrastive loss

KL divergence

sparsity penalty

latent regularization

10. 学習手順

10.1 Optimizer

optimizer = Adam
learning_rate = 0.001
beta1 = 0.9
beta2 = 0.999
eps = 1e-8
weight_decay = 0

learning rate schedulerは使用しない。

10.2 学習条件

epochs = 50
batch_size = 128

Trainのみshuffleする。

Train:
  shuffle = true
  drop_last = false

Validation:
  shuffle = false
  drop_last = false

Test:
  shuffle = false
  drop_last = false

Train DataLoaderの順序は loader_seed によって決定する。

early stoppingおよびgradient clippingは使用しない。

10.3 Checkpoint

最低限以下を保存する。

initial.pt
final.pt

initial.pt は学習開始前の状態とする。

final.pt は50 epoch終了後の状態とする。

Experiment 001の主解析対象は final.pt とする。

Validation lossによってbest checkpointを選択しない。

10.4 Validation

各epoch終了後にValidation lossを測定する。

Validationは、

Autoencoderのparameter更新

early stopping

baseline checkpoint選択

には使用しない。

10.5 失敗run

学習失敗も正式なrunとして保存する。

結果確認後に同一runの設定を書き換えて再実行してはならない。

条件変更が必要な場合は、新しいDecisionおよび新しいrunとして扱う。

11. 潜在表現の保存

initial.pt と final.pt の両方について、

Train

Validation

Test

すべての潜在表現を保存する。

例：

latent_vectors/
├── initial/
│   ├── train.csv
│   ├── validation.csv
│   └── test.csv
└── final/
    ├── train.csv
    ├── validation.csv
    └── test.csv

各行には最低限、

sample_id
latent_0
...
latent_31
color
shape
x
y
size
rotation

を含める。

評価metadataは解析のために付加するものであり、Autoencoder学習へ逆流させてはならない。

12. 解析

12.1 PCA

Test latentをPCAで2次元および3次元へ射影する。

色別・形別の可視化では同一のPCA射影座標を使用する。

PCAは探索的可視化としてのみ使用し、Experiment 001の成功判定には使用しない。

initial.pt と final.pt の両方について同一手順を適用する。

12.2 線形プローブ

Encoderを完全に固定し、潜在表現のみからcolorおよびshapeを予測する。

color probe:
  latent → multinomial logistic regression → 3 classes

shape probe:
  latent → multinomial logistic regression → 3 classes

hidden layerは使用しない。

split

Train latent:
  probe training

Validation latent:
  regularization selection

Test latent:
  final evaluation

正則化候補

L2正則化を使用する。

C ∈ {0.01, 0.1, 1, 10, 100}

Validation accuracyが最大となるCを採用する。

同率の場合は最小のCを採用する。

評価指標

最低限、

train_accuracy
validation_accuracy
test_accuracy
balanced_accuracy
confusion_matrix
chance_level

を保存する。

chance levelはcolor、shapeともに 1/3 とする。

initial.pt と final.pt に完全に同じprobe手順を適用する。

probeの勾配をEncoderへ逆伝播してはならない。

12.3 距離解析

Test splitの全ユニークペアを使用する。

Testサンプル900件の場合、

900 choose 2 = 404550 pairs

となる。

自己ペアおよび順序違いの重複ペアは含めない。

各ペアを以下の4種類へ分類する。

same_color_same_shape
same_color_different_shape
different_color_same_shape
different_color_different_shape

主距離

主解析には、Train latent統計で各次元を標準化したEuclidean距離を使用する。

z' = (z - mean_train) / std_train

std < 1e-8 の次元は標準化距離から除外する。

initial.pt と final.pt は、それぞれ自身のTrain latentから標準化統計を計算する。

補助距離

raw Euclidean distanceも保存する。

統計

各カテゴリについて、

count
mean_distance
median_distance
standard_deviation
bootstrap_95_percent_CI_for_mean

を保存する。

さらに、

same_color
different_color
same_shape
different_shape

の集約値を保存する。

BootstrapはTest sample単位で1,000回行い、analysis_seed を使用する。

13. コントロール

13.1 未学習Encoder

initial.pt に対して、

PCA

距離解析

線形プローブ

を学習済みEncoderと同じ方法で実施する。

これにより、学習前から存在していた構造と学習によって強化された構造を区別する。

13.2 Pixel baseline

Pixel baselineは必須とする。

Simple image statistics baseline

以下の特徴量を使用する。

mean_R
mean_G
mean_B
std_R
std_G
std_B
foreground_fraction

foreground_fraction は、

R + G + B > 0

を満たすpixelの割合とする。

Raw pixel linear baseline

画像を [0,1] に正規化し、

3 × 64 × 64
→ flatten
→ 12288 dimensions

として線形分類器へ入力する。

標準化

Train splitの統計のみを使用する。

x' = (x - mean_train) / std_train

std < 1e-8 のfeatureは除外する。

分類器

線形プローブと同様のmultinomial logistic regressionを使用する。

C ∈ {0.01, 0.1, 1, 10, 100}

Trainで学習、ValidationでC選択、Testで最終評価する。

colorとshapeを別々に評価する。

Pixel baselineは結果解釈のためのcontrolであり、Autoencoderの学習条件へ影響させてはならない。

14. 成功条件

Experiment 001は「概念核の存在」を証明しない。

成功条件は、

再構成学習によって、学習前には弱かったcolorまたはshapeに対応する再現可能な規則的潜在構造が形成されたか

を判定するためのものである。

正式baselineは5 seedで実施する。

14.1 主判定：線形プローブ

属性 A ∈ {color, shape} について、

probe_delta_A
=
final_encoder_test_accuracy
-
initial_encoder_test_accuracy

を定義する。

その属性について以下をすべて満たすこと。

5 seed中4 seed以上で probe_delta_A > 0

5 seedの probe_delta_A 中央値が >= 0.10

final Encoder Test accuracyの5 seed中央値が >= 0.70

14.2 確認判定：距離解析

colorについて、

distance_contrast_color
=
mean(different_color_distance)
-
mean(same_color_distance)

shapeについて、

distance_contrast_shape
=
mean(different_shape_distance)
-
mean(same_shape_distance)

とする。

主距離であるstandardized Euclideanを使用する。

同じ属性について以下をすべて満たすこと。

final Encoderで5 seed中4 seed以上 distance_contrast_A > 0

5 seed中央値で distance_contrast_final > distance_contrast_initial

14.3 Experiment判定

SUCCESS

colorまたはshapeの少なくとも一方が、

線形プローブ条件

距離解析条件

の両方を満たす。

INCONCLUSIVE

規則性または学習前後の改善は観測されたが、事前に定めた成功条件を完全には満たさない。

NO_EVIDENCE

color・shapeとも成功条件を満たさず、学習による一貫した構造強化を確認できない。

14.4 成功判定に使用しないもの

以下は単独では成功条件としない。

PCAの見た目

Pixel baselineとの大小関係

単一seedの高精度

raw Euclidean distanceのみの差

再構成画像の見た目

SUCCESSとなった場合でも、

「概念核を発見した」

とは結論しない。

15. 失敗も結果として扱う

以下を正式な結果として保存する。

colorだけが成功条件を満たした

shapeだけが成功条件を満たした

両方が成功した

INCONCLUSIVEとなった

NO_EVIDENCEとなった

seedによって結果が大きく異なった

再構成は成功したが潜在構造が形成されなかった

学習そのものが失敗した

事前基準を満たさない結果を、実行後に基準変更して成功扱いしてはならない。
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
- 人間との会話
- 現実課題の解決

Experiment 001では、

**「共通構造が自然に形成されるか」**

だけを見る。

---

17. 再現性

すべてのrunについて最低限、

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

を記録する。

用途別seedはmaster seedから決定的に導出するか、独立値として明示的に保存する。

同じ設定とseedから同じデータセット・splitを再生成できること。

run開始時の設定は固定し、途中で研究条件を変更しない。

失敗runも削除しない。
---

18. Experiment 001の最終成果物

1回のrunごとに独立したdirectoryへ保存する。

例：

exp001/
└── runs/
    └── run_001/
        ├── config.yaml
        ├── manifest.json
        ├── dataset_metadata.csv
        ├── checkpoints/
        │   ├── initial.pt
        │   └── final.pt
        ├── training_log.csv
        ├── latent_vectors/
        │   ├── initial/
        │   │   ├── train.csv
        │   │   ├── validation.csv
        │   │   └── test.csv
        │   └── final/
        │       ├── train.csv
        │       ├── validation.csv
        │       └── test.csv
        ├── analysis/
        │   ├── initial/
        │   │   ├── pca_color.png
        │   │   ├── pca_shape.png
        │   │   └── distance_analysis.csv
        │   ├── final/
        │   │   ├── pca_color.png
        │   │   ├── pca_shape.png
        │   │   └── distance_analysis.csv
        │   └── comparisons/
        ├── linear_probe_results.json
        ├── pixel_baseline_results.json
        ├── reconstruction_grid.png
        └── report.md

既存runを上書きしてはならない。

18.1 config.yaml

実際にrunで使用した承認済み条件を保存する。

最低限、

experiment_id
run_id
git_commit

seeds:
  master
  generation
  split
  model
  loader
  probe
  analysis

dataset:
  image_size
  samples_per_combination
  colors
  shapes
  position_range
  size_range
  rotation_range
  color_variation
  rendering
  split

model:
  architecture
  latent_dim
  parameter_count

training:
  epochs
  batch_size
  optimizer
  learning_rate
  loss_function

analysis:
  probe
  distance
  pixel_baseline

を含める。

run開始後にこの設定を書き換えない。

18.2 dataset_metadata.csv

全9,000サンプルについて最低限、

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

を保存する。

18.3 checkpoints/

initial.pt と final.pt を必須とする。

checkpointには可能な限り、

model_state_dict
optimizer_state_dict
epoch
training_loss
validation_loss
model_configuration

を保存する。

18.4 training_log.csv

1 epochにつき1行として、

epoch
training_loss
validation_loss
learning_rate

を必須項目とする。

18.5 latent_vectors/

initial/final × train/validation/test の6種類を保存する。

各行は sample_id により dataset_metadata.csv と対応可能であること。

18.6 PCA成果物

initial / finalそれぞれについて、

pca_color.png
pca_shape.png

を保存する。

色用・形用画像では同一PCA座標を使用する。

可能であればPCA座標およびexplained varianceもmachine-readable形式で保存する。

18.7 距離解析成果物

initial / finalそれぞれについて、

standardized Euclidean

raw Euclidean

の結果を保存する。

最低限、

category
count
mean_distance
median_distance
standard_deviation
bootstrap_ci_lower
bootstrap_ci_upper

を含める。

標準化に使用したTrain mean/stdおよび除外次元も保存する。

18.8 linear_probe_results.json

initial / finalそれぞれについてcolor・shapeの、

selected_C
train_accuracy
validation_accuracy
test_accuracy
balanced_accuracy
confusion_matrix
chance_level

を保存する。

候補CごとのValidation結果も保存する。

18.9 pixel_baseline_results.json

以下2種類についてcolor・shape評価結果を保存する。

simple_image_statistics
raw_pixel_linear

linear probeと同じsplit、C候補、選択規則、指標を使用する。

18.10 再構成品質

再構成学習が成立したか確認するため、

Train reconstruction loss

Validation reconstruction loss

Test reconstruction loss

固定sample_idによる reconstruction_grid.png

を保存する。

再構成品質そのものはExperiment 001の成功条件には使用しない。

18.11 report.md

最低限以下を含める。

1. 実験条件

データセット、モデル、seed、学習条件を記録する。

2. 学習結果

Train / Validation / Test再構成結果を記録する。

3. 線形プローブ

initial / finalおよびcolor / shapeを比較する。

4. 距離解析

主距離と補助距離の結果を記録する。

5. Pixel baseline

latent probeとの比較を記録する。

6. PCA

探索的可視化として記録する。

7. 成功条件の判定

各attributeについて事前基準を機械的に評価する。

8. 観測

測定された事実のみを記述する。

9. 解釈

観測から考えられる説明を記述する。

10. 限界

交絡要因や、この実験だけでは結論できない事項を記述する。

11. 次の実験への示唆

Experiment 002以降で検証すべき事項を記録する。

最終判定は、

SUCCESS
INCONCLUSIVE
NO_EVIDENCE

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

---

## Experiment 001の問い

最終的に、この実験が答えるべき問いは以下の一つである。

> **人間が「赤」「青」「円」「四角」といった概念を一切教師として与えなくても、単純な視覚経験を再構成する過程で、それらに対応する共通構造はAI内部に自発的に形成されるのか？**
