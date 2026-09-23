# Experiment 002 questions — PROPOSED

以下はExperiment 001の事後分析から得た**候補質問**であり、Experiment 002の正式仮説・目的・成功条件・データセット・学習目的・評価方法を決定しない。いずれもHumanの判断と将来の事前登録が必要。正式Exp001分類は `INCONCLUSIVE` のまま。出典は [README.md](README.md) の正式artifact。

| 候補質問 | なぜ重要か | Exp001の根拠 | あり得る測定（未承認） |
| --- | --- | --- | --- |
| 色を初期時点で自明に読めない課題にできるか | 学習による増分を測る余地が必要 | initial color probe 0.9867–0.9989、Pixel color 1.0 | 背景・照明・色相変動の下でinitial/final probeを比較 |
| ランダム特徴が強い原因は何か | final精度だけでは学習効果を識別できない | initial shape 0.6822–0.7422 | 複数ランダムEncoder、raw pixel、単純統計の事前登録比較 |
| 未観測の色×形組み合わせへ表現は使えるか | 再利用可能な構造の最小検査になる | Exp001は9組すべてTrainに存在 | 組み合わせhold-outでprobe・再構成・距離を評価 |
| 位置・大きさ・回転などのnuisanceから属性を分離できるか | 現在のshape距離は何に依存するか未確定 | shape contrastは増えたが、その機構は不明 | 同一属性の変換軌道、属性固定の距離、条件付き評価 |
| accuracy以外で形の改善を捉えられるか | 距離は大きく変わりprobe正答率は小変化 | shape距離delta中央値+3.136、probe delta+0.0289 | margin、校正、相関、条件付き距離、表現比較 |
| 標準化Euclidean以外でも結論は保たれるか | colorのraw/標準化距離が食い違う | color正式distance deltaは全負、raw contrastは4/5増加 | whitening、cosine、近傍保存、表現類似度を事前指定して比較 |
| 形関連の構造は分布移動・別課題へ移るか | 距離変化だけでは有用性を示せない | final raw pixel probeはfinal latent probeより高い | 未知のサイズ/位置/背景、凍結Encoderの転移評価 |
| 入力にある情報と学習で得た表現をどう分けるか | Pixel baselineが強い | color Pixel 1.0、shape raw pixel 0.768–0.782 | input/initial/finalの同条件比較、学習量に応じた事前登録評価 |
| 低MSEと黒出力を避けた上でも形距離は強まるか | 距離構造と再構成の関係が未解決 | 各runの保存再構成9例がほぼ黒、test MSE約0.028 | 全色×形の再構成品質、前景/背景別損失、ゼロ画像基準との比較 |
| 変換の構造や不変性を直接測れるか | 静的なクラスタや線形probeだけでは概念核候補の再利用性を捉えにくい | PCAは探索的、距離は静的ペア集約 | 属性固定の変換追跡、未見変換での表現安定性 |

特に、再構成がほぼ黒となる条件と初期特徴の強さを先に切り分ける必要がある。実験002の閾値は、Experiment 001の結果に合わせて遡及的に変更せず、新しい問いに合わせて**実行前に**Humanが承認する。
