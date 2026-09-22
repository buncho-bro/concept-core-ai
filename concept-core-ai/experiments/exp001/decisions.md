# Experiment 001 Decisions

## DEC-001 Reconstruction Loss
Status: SUPERSEDED
Superseded by: DEC-B05

Question:

Autoencoderの再構成損失として何を使用するか。

Candidates:

- MSE
- BCE
- L1

Proposal:

MSE

Reason:

RGB画像を0〜1の連続値として扱う単純なbaselineとして
実装が容易である。

Decision:

## DEC-B01 — Success Criteria
Status: APPROVED
Source: review/BLOCKERS.md#B-01

Experiment 001の成功条件を以下とする。

scope:
  Experiment 001は概念核の存在を証明しない。
  学習によって概念核候補となり得る
  再現可能な潜在構造が形成されたかを判定する。

seeds:
  count: 5

attributes:
  - color
  - shape

primary_metric:
  linear_probe_test_accuracy

各attribute Aについて:

  probe_delta_A:
    final_encoder_test_accuracy
    -
    initial_encoder_test_accuracy

probe_success_conditions:
  - 5 seed中4 seed以上で probe_delta_A > 0
  - probe_delta_A の5 seed中央値 >= 0.10
  - final test accuracy の5 seed中央値 >= 0.70

confirmatory_metric:
  standardized_euclidean_distance

distance_contrast_A:

  colorの場合:
    mean(different_color)
    -
    mean(same_color)

  shapeの場合:
    mean(different_shape)
    -
    mean(same_shape)

distance_success_conditions:
  - final Encoderについて、
    5 seed中4 seed以上で distance_contrast_A > 0
  - distance_contrast_A の5 seed中央値について、
    final > initial

experiment_success:
  colorまたはshapeの少なくとも一方が、
  probe_success_conditionsと
  distance_success_conditionsの両方を満たす。

result_categories:

  SUCCESS:
    少なくとも1属性が全成功条件を満たす。

  INCONCLUSIVE:
    規則性または改善は観測されたが、
    全成功条件を満たさない。

  NO_EVIDENCE:
    color/shapeとも成功条件を満たさず、
    学習による一貫した構造強化を確認できない。

PCA:
  成功判定には使用しない。
  exploratory visualizationとしてのみ使用する。

pixel_baseline:
  成功判定の必須閾値には使用しない。
  結果の解釈および交絡確認に使用する。

interpretation_constraints:
  - SUCCESSでも「概念核を発見した」とは結論しない。
  - attributeごとの結果を分離して報告する。
  - 基準未達の結果を成功として再解釈しない。
  - 結果を確認した後に閾値を変更しない。

## DEC-B02 — Dataset Generation
Status: APPROVED
Source: review/BLOCKERS.md#B-02

Experiment 001の人工画像生成条件を以下とする。

image:
  width: 64
  height: 64
  channels: RGB
  background: [0, 0, 0]

colors:
  red:   [230, 25, 25]
  green: [25, 230, 25]
  blue:  [25, 25, 230]

color_variation:
  distribution: discrete_uniform
  range: [-10, +10]
  per_channel: independent

position:
  center_x: U_integer(26, 38)
  center_y: U_integer(26, 38)

size:
  definition: circumradius_px
  distribution: U_integer(12, 16)

rotation:
  circle: 0
  triangle: U(0, 360)
  square: U(0, 360)
  unit: degree

rendering:
  fill: solid
  outline: none
  supersampling: 4
  final_resolution: 64x64

constraints:
  - 図形全体が画像内に存在すること
  - clippingを許可しない
  - 背景は変動させない
  - 実行時augmentationを使用しない

## DEC-B03 — Dataset Split
Status: APPROVED
Source: review/BLOCKERS.md#B-03

Experiment 001のデータ分割を以下とする。

基本単位:
- 9種類の color × shape 組み合わせごとに独立して分割する。
- 各組み合わせは1000サンプル。

split:
- Train: 800 / combination
- Validation: 100 / combination
- Test: 100 / combination

total:
- Train: 7200
- Validation: 900
- Test: 900

procedure:
1. B-02に従って全9000サンプルを生成する。
2. 各サンプルへ一意なsample_idを付与する。
3. 各color × shapeグループ内でsample_idを
   split_seedを使用して決定的にshuffleする。
4. 先頭800をTrain、次の100をValidation、
   最後の100をTestとする。
5. splitをdataset_metadata.csvへ固定して保存する。

randomness:
- split_seedはgeneration_seedとは独立させる。
- 同一設定・同一seedから同一splitを再現できること。

constraints:
- Train / Validation / Testは相互排他的。
- 3 splitの和集合は全9000サンプルと一致する。
- 各splitに9種類すべての組み合わせを含める。
- Experiment 001では組み合わせholdoutを行わない。

usage:
- Train:
  Autoencoderの学習に使用する。

- Validation:
  学習状態の確認および、
  事前承認された設定選択にのみ使用可能。

- Test:
  最終評価専用。
  Autoencoderの学習・設定選択には使用しない。

## DEC-B04 — Autoencoder Architecture
Status: APPROVED

Experiment 001のbaselineモデルとして
Convolutional Autoencoderを使用する。

input:
  shape: [3, 64, 64]
  dtype: float32
  range: [0.0, 1.0]
  normalization: RGB / 255

encoder:

  Conv2d:
    in: 3
    out: 32
    kernel: 4
    stride: 2
    padding: 1
  ReLU

  Conv2d:
    in: 32
    out: 64
    kernel: 4
    stride: 2
    padding: 1
  ReLU

  Conv2d:
    in: 64
    out: 128
    kernel: 4
    stride: 2
    padding: 1
  ReLU

  Conv2d:
    in: 128
    out: 256
    kernel: 4
    stride: 2
    padding: 1
  ReLU

  Flatten

  Linear:
    in: 4096
    out: latent_dim

latent:
  latent_dim: 32
  activation: none
  shape: [32]

decoder:

  Linear:
    in: latent_dim
    out: 4096
  ReLU

  Reshape:
    [256, 4, 4]

  ConvTranspose2d:
    in: 256
    out: 128
    kernel: 4
    stride: 2
    padding: 1
  ReLU

  ConvTranspose2d:
    in: 128
    out: 64
    kernel: 4
    stride: 2
    padding: 1
  ReLU

  ConvTranspose2d:
    in: 64
    out: 32
    kernel: 4
    stride: 2
    padding: 1
  ReLU

  ConvTranspose2d:
    in: 32
    out: 3
    kernel: 4
    stride: 2
    padding: 1
  Sigmoid

normalization_layers:
  none

dropout:
  none

constraints:
  - latent_dimはconfigから変更可能にする。
  - Experiment 001 baselineではlatent_dim=32を使用する。
  - latentには正規化・活性化を加えない。
  - 色・形その他の評価metadataをモデルへ入力しない。
  - architectureを結果確認後に変更して同一baselineとして扱わない。
  - モデルの総parameter数を記録する。

## DEC-B05 — Training Procedure
Status: APPROVED

Experiment 001 baselineの学習条件を以下とする。

objective:
  type: image_reconstruction_only

loss:
  function: MSE
  reduction: mean

optimizer:
  type: Adam
  learning_rate: 0.001
  beta1: 0.9
  beta2: 0.999
  eps: 1e-8
  weight_decay: 0

training:
  epochs: 50
  batch_size: 128

train_loader:
  shuffle: true
  drop_last: false
  randomness: loader_seed

validation_loader:
  shuffle: false
  drop_last: false

test_loader:
  shuffle: false
  drop_last: false

learning_rate_scheduler:
  none

early_stopping:
  none

gradient_clipping:
  none

regularization:
  weight_decay: none
  latent_regularization: none
  sparsity_penalty: none
  KL_divergence: none
  contrastive_loss: none

checkpoint:
  initial:
    学習開始前のモデル

  final:
    epoch 50終了時のモデル

primary_analysis_checkpoint:
  final.pt

validation:
  - 各epoch終了後にvalidation lossを測定する。
  - Autoencoderのparameter updateには使用しない。
  - early stoppingには使用しない。
  - baselineのcheckpoint選択には使用しない。

logging:
  per_epoch:
    - epoch
    - training_loss
    - validation_loss
    - learning_rate

failure_policy:
  - 学習失敗もrunとして保存する。
  - 結果を確認した後に同一runの設定を書き換えない。
  - 学習条件を変更する場合は新しいDecisionと新しいrunを作る。

constraints:
  - 学習目的は画像再構成のみ。
  - color/shape metadataを損失計算に使用しない。
  - latent構造を直接誘導する損失を使用しない。

## DEC-B06 — Linear Probe
Status: APPROVED

Experiment 001の線形プローブを以下とする。

purpose:
  学習済み潜在表現からcolorおよびshapeが
  どの程度線形に読み出せるかを測定する。

encoder:
  frozen: true
  gradient_from_probe: prohibited

latent:
  - Train / Validation / Testすべてについて抽出する。
  - initial.ptとfinal.ptの両方について抽出する。
  - probe学習前にEncoder出力をdetachする。

probes:
  color:
    type: multinomial_logistic_regression
    classes: [red, green, blue]

  shape:
    type: multinomial_logistic_regression
    classes: [circle, triangle, square]

  hidden_layers: none

training:
  train_split: Train
  validation_split: Validation
  final_evaluation_split: Test

regularization:
  type: L2
  C_candidates:
    - 0.01
    - 0.1
    - 1
    - 10
    - 100

selection:
  criterion: highest_validation_accuracy
  tie_break:
    select_smallest_C

randomness:
  seed: probe_seed

evaluation:
  primary_metric: test_accuracy

  additional_metrics:
    - train_accuracy
    - validation_accuracy
    - balanced_accuracy
    - confusion_matrix

  chance_level:
    color: 1/3
    shape: 1/3

controls:
  - initial.ptとfinal.ptに同一probe手順を適用する。
  - split、C候補、選択規則、評価指標を同一にする。

constraints:
  - Test latentをprobeの学習または設定選択に使用しない。
  - probeからEncoderへ勾配を返さない。
  - color/shape probeは独立して学習する。
  - probe性能だけを根拠に概念核形成を断定しない。

## DEC-B07 — Distance Analysis
Status: APPROVED

Experiment 001のlatent距離解析を以下とする。

analysis_split:
  Test

pair_selection:
  use_all_unique_pairs: true
  include_self_pairs: false
  duplicate_ordered_pairs: false

pair_categories:
  - same_color_same_shape
  - same_color_different_shape
  - different_color_same_shape
  - different_color_different_shape

distance_metrics:

  primary:
    name: standardized_euclidean

    standardization:
      statistics_source: Train latent
      per_dimension: true

      formula:
        z' = (z - mean_train) / std_train

      near_zero_std_threshold: 1e-8
      near_zero_std_action:
        exclude_dimension

  secondary:
    name: raw_euclidean

statistics_per_category:
  - count
  - mean_distance
  - median_distance
  - standard_deviation
  - bootstrap_95_percent_CI_for_mean

bootstrap:
  iterations: 1000
  resampling_unit: test_sample
  seed: analysis_seed

additional_aggregates:
  color:
    - same_color
    - different_color

  shape:
    - same_shape
    - different_shape

controls:
  - initial.ptとfinal.ptの両方に同一手順を適用する。
  - initial/finalそれぞれのTrain latentから
    個別にstandardization統計を計算する。

artifacts:
  - categoryごとの統計
  - raw Euclidean結果
  - standardized Euclidean結果
  - standardizationに使用したmean/std
  - 除外されたnear-zero variance次元
  - bootstrap CI
  - initial/final比較可能な形式

constraints:
  - Test labelは距離カテゴリ分類にのみ使用する。
  - Testデータからstandardization統計を推定しない。
  - 距離尺度を結果確認後に変更して主解析として扱わない。
  - 距離差だけを根拠に概念核形成を断定しない。

## DEC-B08 — Pixel Baseline
Status: APPROVED

Experiment 001ではPixel baselineを必須とする。

目的:
  潜在表現から読み出されたcolor/shape情報が、
  元画像の単純な統計または生pixel空間でも
  容易に読み出せる情報ではないかを比較する。

baseline_1:
  name: simple_image_statistics

  features:
    - mean_R
    - mean_G
    - mean_B
    - std_R
    - std_G
    - std_B
    - foreground_fraction

  foreground_definition:
    RGB sum > 0

baseline_2:
  name: raw_pixel_linear

  input:
    RGB image normalized to [0,1]

  transform:
    flatten to 12288 dimensions

feature_standardization:
  statistics_source: Train

  formula:
    x' = (x - mean_train) / std_train

  near_zero_std_threshold: 1e-8
  near_zero_std_action: exclude_feature

classifier:
  type: multinomial_logistic_regression
  hidden_layers: none

regularization:
  type: L2

  C_candidates:
    - 0.01
    - 0.1
    - 1
    - 10
    - 100

split_usage:
  Train:
    classifier training

  Validation:
    C selection

  Test:
    final evaluation only

selection:
  criterion: highest_validation_accuracy
  tie_break:
    select_smallest_C

targets:
  - color
  - shape

metrics:
  - train_accuracy
  - validation_accuracy
  - test_accuracy
  - balanced_accuracy
  - confusion_matrix

chance_level:
  color: 1/3
  shape: 1/3

comparison:
  - simple statistics baseline
  - raw pixel linear baseline
  - initial Encoder latent probe
  - final Encoder latent probe

constraints:
  - Testをclassifier trainingまたは設定選択に使用しない。
  - Pixel baselineはAutoencoderの学習へ影響させない。
  - Pixel baselineの結果を見てAutoencoderの研究条件を同一run内で変更しない。
  - latentがPixel baselineを上回ること自体を、
    この段階では成功条件にしない。
  - Pixel baselineだけを根拠に概念核の有無を判断しない。
