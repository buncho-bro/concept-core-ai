# Color analysis

**Experiment-level classification: INCONCLUSIVE**（属性別に正式分類を付け直さない）。出典は `aggregate_metrics.json` の `runs[*].primary.color` と `attributes.color`、各run ZIPの `evaluation/summary.json`、および `spec.md` §4, §13, §17。ZIPの所在は [README.md](README.md) を参照。

## CONFIRMATORY FINDINGS

contrastは標準化Test latentの `mean(different_color) − mean(same_color)`、deltaはfinal−initial。initialとfinalはそれぞれのTrain latent統計で標準化される。

| seed | initial probe | final probe | probe delta | initial contrast | final contrast | distance delta |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1001 | 0.997778 | 0.997778 | 0.000000 | 1.120360 | 0.140137 | −0.980224 |
| 1002 | 0.998889 | 1.000000 | +0.001111 | 1.833064 | 0.262411 | −1.570652 |
| 1003 | 0.991111 | 1.000000 | +0.008889 | 1.325523 | 0.041817 | −1.283705 |
| 1004 | 0.986667 | 1.000000 | +0.013333 | 1.131898 | 0.360935 | −0.770964 |
| 1005 | 0.991111 | 0.988889 | −0.002222 | 0.975349 | 0.530095 | −0.445253 |

Probe改善は3/5、中央値+0.001111。final accuracy中央値1.0。final contrastは5/5正だが、distance deltaは5/5負、中央値−0.980224。色の正式SUCCESS条件は満たさない（`aggregate_metrics.attributes.color.conditions`）。

## EXPLORATORY INTERPRETATIONS

### Initial separabilityとceiling

色は学習前から0.9867以上の精度で読める。RGBの各channel差が大きく、背景は固定の黒、前景は単色で、色×形9組を含む単純な分布である。ランダム畳み込み投影が入力の色差を線形読出し可能なまま残した可能性がある。ただし原因を切り分ける介入はない。initial精度がほぼ上限のため、`final−initial` の改善余地は小さい。これは測定上のceiling効果という解釈であり、事前登録した0.10閾値が誤りだったとの事後判定ではない（`spec.md` §4, §8; `aggregate_metrics`）。

### 線形可読性と距離構造の不一致

色ラベルはfinal latentから線形に読める一方、標準化Euclidean距離での色contrastは全seedで縮む。考え得る説明は、形や他の変動に比べ色の距離寄与が小さくなった、クラス境界は維持されたままクラス内・クラス間距離が変わった、initial/final別々の標準化が座標ごとの寄与を変えた、などである。どの説明が支配的かは本実験だけでは決められない。補助的raw Euclidean contrastは4/5 seedで増え、1/5で減る（各ZIP `evaluation/summary.json`）。rawと標準化距離の食い違いは、幾何の記述が尺度選択に依存することを示す。正式判定には標準化距離のみを使う。

### Pixel baselineとPCA

simple image statistics、raw pixel linearのcolor test accuracyはいずれも全5 seedで1.0（`aggregate_metrics.runs[*].pixel_baseline_summary`）。色情報が入力で容易に得られることは確認できるが、autoencoderによる新規表現学習の証拠ではない。PCA 2Dではinitial/finalとも色の点群が重なり、seed 1001などではfinalの色別分離はむしろ視覚的に弱い（各ZIP `evaluation/pca_initial/pca_2d_color.png`, `pca_final/pca_2d_color.png`）。高い32次元probe精度と2次元PCAの重なりは矛盾しない。PCAを成功判定に使わない。

## 限界

色は3種のみで色相・照明・背景の変化を試していない。学習前の可読性とfinal精度から「色概念を再構成から学んだ」とは言えない。再構成画像は全runで赤い円だけを選んでおり、色別の再構成品質を比較できない。追加の機構解釈は `CROSS_METRIC_ANALYSIS.md` と `LIMITATIONS.md` に分けた。
