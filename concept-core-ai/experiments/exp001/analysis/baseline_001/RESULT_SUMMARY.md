# Result summary

**Experiment-level classification: INCONCLUSIVE**。正式seed `1001–1005` は同一実行コミット `e9791b2`、すべて `VALID`、評価flagなし、各1回の完了runである（`RUN_SUMMARY`, `RUN_MANIFEST`, `baseline_manifest`）。正式分類を変更しない。

## CONFIRMATORY FINDINGS

事前登録条件（`spec.md` §17）は、各属性についてprobe deltaが4/5 seedで正、中央値が **0.10以上**、final accuracy中央値が **0.70以上**、final距離contrastが4/5 seedで正、距離delta中央値が正、という条件をすべて満たした場合のみ `SUCCESS` とする。色または形のprobe deltaまたは距離deltaの中央値が正なら、`SUCCESS` 不成立時は `INCONCLUSIVE` とする。

| 属性 | probe delta正 | probe delta中央値 | final accuracy中央値 | final contrast正 | distance delta中央値 | 正式SUCCESS |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| color | 3/5 | +0.001111 | 1.000000 | 5/5 | −0.980224 | 不成立 |
| shape | 4/5 | +0.028889 | 0.745556 | 5/5 | +3.136271 | 不成立 |

色はprobe改善数と改善量、距離deltaが条件未達。形はprobe改善方向・final accuracy・距離条件を満たすが、probe delta中央値が0.10未満。shapeの正のprobe・距離中央値により、確定済み `INCONCLUSIVE` と事前登録条件は整合する。表の数値は `aggregate_metrics.json` の `attributes` と `runs[*].primary` による。ここでの照合は既存判定の理由の確認であり、新しい分類ではない。

## EXPLORATORY INTERPRETATIONS

色のinitial probe accuracyは0.9867–0.9989で、学習前からほぼ線形に読めた。したがってfinal accuracyが高いことは、再構成による色概念の新規学習を示さない。黒背景と分離の大きいRGB値を持つ単純画像では、ランダム畳み込み特徴でも色情報が読みやすい可能性がある（`spec.md` §4、`aggregate_metrics.runs[*].primary.color`）。

形のinitial accuracyも0.6822–0.7422である一方、標準化距離contrastは全seedで0.350–0.753から3.560–4.278へ増えた。これは、このデータと距離定義の下で形に関連する潜在幾何が学習後に一貫して変化したという観測を支持する。形概念の獲得や汎化の証明にはならない（`aggregate_metrics.runs[*].primary.shape`）。

重要な留保として、保存された各runの9枚の再構成例は、いずれも**赤い円のみ**で、final出力は数値上ほぼ黒である。initial→finalのtest MSEは約0.239–0.244→0.02795–0.02811へ低下したが、図形を復元できたことは示さない。50 epochのvalidation lossも初回末からほぼ横ばい。`VALID` は手続き・解析の成立であり、意味のある画像再構成の成功を意味しない（各ZIPの `reconstruction_losses.json`, `training.csv`, `reconstruction.npz`, `metadata.csv`）。

総合すると、学習前の強い色の可読性と、学習後に一貫して強まる形の距離構造は確認できる。一方、形の線形probe改善は正式閾値に届かず、再構成の代表例は黒出力である。潜在構造の変化は実在する測定結果だが、その機構、機能的有用性、概念核としての再利用可能性は未検証である。
