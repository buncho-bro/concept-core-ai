# Shape analysis

**Experiment-level classification: INCONCLUSIVE**。出典は `aggregate_metrics.json` の `runs[*].primary.shape` と `attributes.shape`、各seed ZIPの `evaluation/distance_{initial,final}.json`、`evaluation/summary.json`。ZIPの所在は [README.md](README.md) を参照。

## CONFIRMATORY FINDINGS

標準化Test latentに対し、shape contrast = `mean(different_shape) − mean(same_shape)`。initial/finalの標準化は各状態のTrain統計を別々に用いる（`spec.md` §17、`decisions.md` DEC-B07）。

| seed | initial probe | final probe | probe delta | initial contrast | final contrast | distance delta |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1001 | 0.720000 | 0.745556 | +0.025556 | 0.587013 | 4.008968 | +3.421954 |
| 1002 | 0.706667 | 0.752222 | +0.045556 | 0.518736 | 3.560055 | +3.041319 |
| 1003 | 0.682222 | 0.762222 | +0.080000 | 0.350229 | 4.277557 | +3.927327 |
| 1004 | 0.694444 | 0.723333 | +0.028889 | 0.530586 | 3.651860 | +3.121274 |
| 1005 | 0.742222 | 0.738889 | −0.003333 | 0.752755 | 3.889026 | +3.136271 |

Probe deltaは4/5で正、中央値+0.028889、final accuracy中央値0.745556。final contrastとdistance deltaは5/5で正、距離delta中央値+3.136271。probe改善量の事前登録閾値0.10には届かないので、形も正式SUCCESSは成立しない（`aggregate_metrics.attributes.shape.conditions`）。seed間のdistance deltaは+3.041–+3.927、標準偏差（ddof=0）0.3255である。これを「この5 runで一貫した形関連の距離構造増加」と表現することは証拠に沿う。

## EXPLORATORY INTERPRETATIONS

### 変化の内訳

各ZIPの `evaluation/distance_{initial,final}.json` に記録された平均距離を見ると、initialのsame-shapeは7.335–7.468、different-shapeは7.789–8.088。finalのsame-shapeは3.652–4.377へ下がり、different-shapeは7.778–8.007程度にとどまる。したがって、標準化距離でのcontrast増加は主に**同形ペアの距離縮小**と整合する。クラス間距離の拡大を主因とする記述は支持されない。

finalのsame-shape平均距離のsample bootstrap 95% CIはseed順に `[3.833,4.161]`, `[4.224,4.542]`, `[3.516,3.793]`, `[4.066,4.421]`, `[3.670,4.096]`。different-shapeは `[7.688,8.329]`, `[7.634,8.250]`, `[7.605,8.297]`, `[7.583,8.242]`, `[7.390,8.138]` で、各seed内では区間が重ならない（各ZIP `evaluation/distance_final.json`; 1000/1000有効反復）。ただし、これは各平均の区間であり、**contrastやinitial→final差の直接のCIではない**。ペアを独立サンプルとして扱った有意性主張もしない。

### Probeとの相違

初期Encoderでもshape test accuracyは0.6822–0.7422あり、ランダム畳み込み特徴に形の線形可読性がある。再構成学習後の距離構造が大きく変わっても、既存の線形決定境界で正答数が少ししか変わらないことはあり得る。距離は全ペアの相対配置を、accuracyは各sampleの正誤を測る。今回観測された同形ペアの距離縮小は前者を強く動かし得るが、後者の0.10改善を保証しない。非線形な変形、クラス内圧縮、accuracyの粗い刻み（test 900件）も候補だが、どれが主要因かは未確定。

### Pixel baselineとPCA

shapeのsimple statistics baselineは0.7222–0.7489、raw pixel linearは0.7678–0.7822。raw pixel linearは全5 seedでfinal latent probe（0.7233–0.7622）を上回る（`aggregate_metrics.runs[*].pixel_baseline_summary`）。形情報は入力そのものからかなり容易に読める。latentで距離構造が変わったという観測はPixel baselineだけでは説明できないが、より有用な表現を学んだとも言えない。

2D PCAではinitialの形別点群が重なり、finalでは円・三角形が主成分方向で離れ、四角形は中間に分布する傾向がseed 1001, 1003, 1005などで見える。一方でクラス間の重なりも残る（各ZIP `evaluation/pca_{initial,final}/pca_2d_shape.png`）。これは形距離contrast増加と定性的に整合するが、PCAは32次元情報の2次元投影であり、正式判定や概念核の証明には使わない。

## 解釈の境界

**Observed fact:** 形contrastは全5 seedで増えた。**Plausible interpretation:** 学習後の潜在空間は、このデータの形に関係する近接性が強い。**Unsupported claim:** 人間のような形概念核が形成された、未知の形や組み合わせに転移する、図形の再構成を通じてその構造が得られた、という主張。最後の機構主張には再構成がほぼ黒出力である事実も強い留保となる（`CROSS_METRIC_ANALYSIS.md`）。
