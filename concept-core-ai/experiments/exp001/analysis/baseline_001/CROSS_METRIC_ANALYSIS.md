# Cross-metric analysis

**Experiment-level classification: INCONCLUSIVE**。主要数値は `aggregate_metrics.json` と各ZIP `evaluation/summary.json` による。以下の異なる指標を同じ「概念形成」の尺度と見なさない。

## CONFIRMATORY FINDINGS

| 観点 | Color | Shape |
| --- | --- | --- |
| 学習前の線形読出し | 0.9867–0.9989 | 0.6822–0.7422 |
| 学習後の線形読出し | 0.9889–1.0000 | 0.7233–0.7622 |
| probe delta中央値 | +0.001111、正3/5 | +0.028889、正4/5 |
| 標準化距離contrast変化 | −0.980224中央値、負5/5 | +3.136271中央値、正5/5 |

色は線形読出しの高さを保ちながら正式距離contrastが縮み、形は距離contrastが大きく増えながらprobe改善が小さい。これは指標間の**観測された不一致**であり、どちらかの測定誤りを直ちに意味しない。probeは32次元特徴からの線形分類の正誤、contrastは標準化Euclidean距離の同属性/異属性ペア平均差を測る（`spec.md` §13, §17; `decisions.md` DEC-B07）。

## EXPLORATORY INTERPRETATIONS

### LatentとPixel

Pixel baselineのcolorは両方式で全seed 1.0。shapeはsimple statisticsが0.7222–0.7489、raw pixel linearが0.7678–0.7822で、後者は各seedのfinal latent shape probeを上回る。入力にラベル情報があることと、autoencoderが新しく再利用可能な表現を得たことは別である。raw pixel classifierも評価ラベルを使って訓練する**読出し器**であり、autoencoderの教師信号ではない（`aggregate_metrics.runs[*].pixel_baseline_summary`; `decisions.md` DEC-B08）。

### 距離の尺度依存性

正式指標はinitial/finalをそれぞれのTrain統計で標準化したEuclidean距離である。補助的raw Euclidean color contrastはinitial→finalでseed 1001 `0.168→4.477`、1002 `0.266→0.846`、1003 `0.219→0.156`、1004 `0.190→3.116`、1005 `0.210→20.873`。標準化距離では全seedで色contrastが減る。この食い違いは潜在座標の尺度・分散変化が距離の解釈を左右することを示す。raw値を正式判定に混ぜない（各ZIP `evaluation/summary.json`、`decisions.md` DEC-B07）。

### PCA

2D PCAはinitial/finalを別々にfitする探索的投影であり、軸の向き・大きさを状態間で直接比較できない。形はfinalで主成分方向の分離が目立つ一方、重なりは残る。色は32次元probeがほぼ完全でも2D投影では重なり得る。PCAの見た目とprobe/distanceの一致・不一致は記述できるが、クラスタを概念核と同一視しない（各ZIP `evaluation/pca_{initial,final}/pca_2d_{color,shape}.png`; `spec.md` §12）。

### 学習曲線と再構成

5 runの初期→最終test MSEは順に `0.23905→0.02796`, `0.23954→0.02803`, `0.24355→0.02795`, `0.23972→0.02804`, `0.24411→0.02811`。数値上の低下は全seedで大きい。しかしepoch 1末のvalidation lossは既に `0.02789–0.02848`、epoch 50までほぼ不変で、発散や後半の不安定さは見えない。finalのTrainとValidation lossにも大きな乖離はない。この曲線は早いplateauと整合し、後半の過学習を示す積極的証拠はない（各ZIP `training.csv`, `reconstruction_losses.json`）。

保存された各runの9枚のfinal再構成は、入力が赤い円なのに出力の最大pixel値が `6.7e-6`, `1.14e-4`, `7.0e-5`, `1.85e-4`, `2.3e-7`（seed順、入力は0–1）で、見た目もほぼ黒である。平均pixel値も `1.4e-10–1.2e-8`。MSEの低下を図形・色の再構成成功と解釈できない。黒背景が広い画像へのほぼゼロ出力は低い全pixel MSEと両立する。ただし保存画像は各run **赤い円9枚だけ**なので、全色・全形で同じ出力かはこの画像からは判定できない（各ZIP `reconstruction.npz`, `reconstruction.png`, `metadata.csv`）。

このため、`VALID` は仕様どおり5 runが完了し正式指標が得られたという実行状態である。表現目標や意味のある再構成の成功とは別である。形距離contrastの変化は測定されたが、ほぼ黒の再構成と共存する理由は不明である。「再構成のために形概念を形成した」という因果説明は支持されない。
