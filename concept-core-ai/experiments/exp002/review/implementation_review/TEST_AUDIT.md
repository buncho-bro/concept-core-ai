# TEST_AUDIT

実行: 独立 worktree の merge commit `778e570`、既存の Python 3.12.14 / pytest 8.4.1 / pinned NumPy・PyTorch 等で `pytest tests -q -p no:cacheprovider`。専用一時領域を使用した最終実行は **215 passed, 14 warnings, 0 failed/skipped/errors、90.96 秒**。最初の試行は一時領域のアクセス権により **173 passed, 42 setup errors** となったため、書き込み可能な一時領域に変更して全件を再実行した。formal RUN はなし。一時テストデータは削除済み。

分類: A=独立 oracle、B=回帰、C=統合、D=循環／自己確認、E=不足。

| 領域 | 主なテストと質 | 所見 |
| --- | --- | --- |
| balanced loss / zero / gate | `test_exp002_reconstruction.py` の異なる foreground 面積の手計算値・勾配・pooled 対照（A）、実モデル50 epoch小 fixture（C） | PASS |
| generation / split | `test_exp002_data.py` の独立件数・手続き上の shuffled position（A/B）。生成画像比較の一部は同じ production `rasterize` 同士（D） | 主要 split は PASS、pixel-level 独立 oracle は限定的 |
| leakage | split 拒否、Validation変更時の weights 不変、Held-out変更時の probe fit 不変、Reserved NaN 注入（B/C） | PASS |
| scaler / probe | 手計算 mean/std・除外閾値、選択呼び出しへの Held-out 非混入（A/B）、実 classifier（C） | PASS |
| pair count / contrast | label fixture と手計算カテゴリ数、toy distance の符号（A）。保存済 pair からの contrast 再計算（C、一部 category helper 依存） | PASS |
| bootstrap seed / multiplicity / percentile | SHA-256 を直接計算（A）。乱数列テストの sub-seed は production 関数依存（D 部分）だが別 seed oracle が補完。literal instance pairs、手計算補間・949/950 境界（A） | PASS |
| precedence / success boundaries | 5件の in-memory fixture で全7段、4/5、0.05、0.70、0.80、1.0、警告非阻止を検査（A/B） | 数式・条件順は PASS |
| formal attempt 選定 / performance freeze | duplicate は**渡された5件内**だけを検査。渡されなかった同 seed の別 attempt、RUN前凍結の証跡・拒否の oracle はない（E） | FAIL：REV-002-01/02 |

独立追加確認: production pair helper を使わず組み合わせ数だけから Seen `29,700/30,000/30,000/90,000`、cross `0/60,000/60,000/60,000` を算出。別の非formal in-memory fixture で、同 commit/設定の seed attempt 1件の選択を変えるだけで `INCONCLUSIVE` と `SUCCESS` が両方得られることを確認。
