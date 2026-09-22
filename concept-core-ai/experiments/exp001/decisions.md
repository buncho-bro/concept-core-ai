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

DEC-B02
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
