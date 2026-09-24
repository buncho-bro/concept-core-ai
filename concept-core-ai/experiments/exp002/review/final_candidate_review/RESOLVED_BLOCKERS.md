# RESOLVED_BLOCKERS

| 前回指摘 | 判定 | 理由 |
| --- | --- | --- |
| NB-002-01 | RESOLVED | §12.2–12.4 が各画像・各領域の RGB 要素平均、画像ごとの 0.5/0.5 合成、ミニバッチ内の画像等重み平均を指定。§13–15 は評価・zero baseline・gate に同じ per-image-first 集計を要求し、領域を画像間で先に pooling する方法を禁じる。 |
| NB-002-02 | RESOLVED | §23–24・§28–34 が Seen-only の母集団 600 件／600 件復元抽出、1000 回、重複出現・同一原 sample ID 除外、カテゴリ別欠損、950 境界、percentile 補間を定義。Seen-only と cross に独立した SHA-256 派生 sub-seed と PCG64 Generator を使い、cross の 600→300 抽出順を固定。Held-out-only CI は不要と明記。 |

前回の NB-002-01/02 解消は候補仕様の記述に対する監査判定であり、Human の正式承認を代替しない。
