# VERIFICATION_PLAN

IMPLEMENT 後、少なくとも次を自動検証する。

- `exp002|` の5 master seed・6 purpose seed と2 bootstrap sub-seed の SHA-256 導出、同一 seed/環境での index 列・結果の再現。
- 9 combination×1000 件、図形生成・RGB・4×4 rasterization・追加量子化なし・sample ID 一意性。
- Seen Train/Validation/Test = 4800/600/600、Held-out Test = 300、Reserved = 2700。排他・網羅・各 combination 件数、held-out/Reserved の全学習・選択経路からの遮断。
- モデル層、初期化、FP32、AMP/FP16/BF16/TF32 無効、50 epoch、update 前 initial と終了後 final、ラベル漏洩なし。
- 面積の異なる複数画像の手計算例で foreground/background RGB 要素平均→画像ごと合成→画像等重み batch/dataset 平均を照合。zero baseline と Seen Test gate も同じ順序・閾値境界で照合。
- initial/final frozen Encoder、Seen Train scaler のみ（ddof=0、閾値）、Seen Validation のみの C 選択、Held-out Test 非使用、probe と Pixel baseline の分類器・metrics 条件一致。
- Seen-only unique pair = 179700、4カテゴリ = 29700/30000/30000/90000、cross pair = 180000、3カテゴリ各60000。主距離の Seen Train 標準化、initial/final 別統計、raw は secondary。
- Seen-only と cross の RNG 独立性、各1000反復、指定された抽出数・呼び出し順、出現 multiplicity、同一元 sample ID 除外（Seen-only）、直接 pair resampling/再 fit なし、カテゴリ別 valid 回数・950 境界、2.5/97.5 percentile 線形補間。片方の解析実行順を変えても他方の index 列が不変。
- 9 代表例が該当 Test subset 内の最小 sample ID であり、入力・両再構成・誤差・per-image metrics が対応。
- run status と evaluation flags を分離し、formal 5 run の同一 commit/環境、INVALID→NOT_EVALUATED、EXPERIMENTAL_FAILURE/primary 欠損/gate failure→INCONCLUSIVE、SUCCESS の4/5・中央値境界、正方向 INCONCLUSIVE と NO_EVIDENCE、CI/control warning の非阻止を検証。
- Run-level/Experiment-level 成果物から dataset・split・checkpoint・latent・probe・距離・bootstrap・gate・最終判定を再計算できること。
