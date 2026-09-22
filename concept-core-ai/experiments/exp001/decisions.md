# Experiment 001 Decisions

## DEC-001 Reconstruction Loss

Status: PROPOSED

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

#DEC-B02
Status: APPROVED

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

#DEC-B03
Status: PROPOSED

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

#DEC-B04
Status: PROPOSED

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
