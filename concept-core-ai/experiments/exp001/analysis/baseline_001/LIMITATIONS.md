# Limitations and claim boundaries

**Formal Experiment 001 classification remains: INCONCLUSIVE.** 数値と正式条件は `aggregate_metrics.json`、`spec.md` §17、出典URLは [README.md](README.md) を参照。

## CONFIRMATORY FINDINGS

5 seedはすべて `VALID` で、正式probeと距離指標に欠損はない。shapeの距離deltaは5/5正だが、probe delta中央値+0.028889は事前登録の0.10未満。colorはinitial probeがほぼ上限で、probe改善3/5、標準化距離deltaは5/5負。したがって `INCONCLUSIVE` を維持する（`RUN_MANIFEST`, `aggregate_metrics`）。「0.10が厳しすぎた」と結果を見て閾値を変更しない。将来の事前登録における測定設計の課題としてのみ扱う。

## EXPLORATORY INTERPRETATIONS

| 制約 | 実験結果への影響 |
| --- | --- |
| 人工的で単純なデータ | 黒背景、単色前景、3色・3形、固定64×64画像。自然画像・複雑な概念への外挿はできない。 |
| 全組み合わせを学習 | 色×形9組はTrainにもTestにもある。未知の組み合わせへの合成的汎化は測定していない。 |
| 分布移動・転移課題なし | 背景、照明、色相、形、サイズ、位置、回転分布の外側での安定性や別タスクへの転移は不明。 |
| ランダム初期化も有益 | initial color probe 0.9867–0.9989、shape 0.6822–0.7422。finalの可読性だけでは学習による新規獲得を示せない。 |
| probeの範囲 | 線形読出しとtest accuracyを測る。非線形利用可能性、校正、境界からの距離、再利用性は測らない。accuracyは900件の離散値で、色は天井に近い。 |
| 距離の範囲 | 主指標はTrain統計で標準化したEuclidean距離。尺度・相関・非線形変換に依存し、raw距離とは色で異なる方向になる。クラス内圧縮が有用な表現かは別問題。 |
| 5 seed、単一構成 | seedの変動は見たが、architecture、latent次元32、MSEのみの学習目的を変えていない。一般的な再現性・頑健性は未検証。 |
| PCA | 2D/3Dの探索的投影。高次元分離や概念の形を証明しない。initial/finalで別fitのため軸の直接比較は不可。 |
| 再構成記録の偏り | 保存された画像は各run赤い円9例のみ。これらはほぼ黒出力。色・形別の再構成失敗率を画像だけで比較できない。 |
| 損失の盲点 | 全pixel MSEは大きな黒背景で低くなり得る。低いtest lossと図形の復元は同義ではない。 |

## Supported / unsupported

**支持される観測:** この5 seed・同じデータ分布・事前登録された標準化距離で、shape contrastが一貫して増加した。色は学習前からほぼ完全に線形可読だった。ランダム特徴とPixel baselineはこの単純な課題に対する強い比較対象である。学習後の潜在幾何は属性関連の方向へ変化した。ただし、その変化の機能的価値は未確定（`aggregate_metrics`; 各ZIP `evaluation/summary.json`）。

**もっともらしいが未検証:** 学習がshapeに関係する配置を組織した、同形ペアを圧縮した、色より形が距離を支配するようになった。後二者は距離統計と整合するが、どの計算機構が生んだかは不明。黒出力との関係も未解決（各ZIP `evaluation/distance_final.json`, `reconstruction.npz`）。

**支持されない主張:** 概念核の証明、人間的な概念形成、色概念のゼロからの学習、形表現のデータセット外汎化、未知の色×形組み合わせへの転移、nuisance変数への不変性、潜在構造が単一ベクトル・クラスタであること、画像を忠実に再構成できたこと。これらをExperiment 001の結論に含めない。
