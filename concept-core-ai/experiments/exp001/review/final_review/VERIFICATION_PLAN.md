# VERIFICATION_PLAN

IMPLEMENT後、最低限以下を自動検証する。

1. 画像が9,000件生成され、RGB・位置・size・rotation・非clipping条件を満たす。
2. 同一設定・seedから画像およびmetadata hashが再現される。
3. 各組み合わせがTrain 800、Validation 100、Test 100である。
4. 3 splitが相互排他的で、和集合が全9,000件になる。
5. Autoencoderのbatch・forward・loss経路にcolor/shapeが渡らない。
6. モデル構造、bias、parameter数、activationが承認済み仕様と一致する。
7. `initial.pt`がoptimizer update前、`final.pt`が50 epoch後である。
8. Validation/Testでparameter更新が発生しない。
9. initial/final × Train/Validation/Testの6 latent集合が完全で、`sample_id`が一致する。
10. probeのscalerがTrainだけでfitされる。標準化しない決定の場合は標準化処理が存在しないことを検査する。
11. C選択がValidationだけを使い、同率時に最小Cを選ぶ。
12. Testへ初めてアクセスする時点でprobe設定が固定済みである。
13. Encoderへprobe gradientが到達しない。
14. Testのunique pair数が404,550件になる。
15. 距離カテゴリ件数が以下と一致する。
    - same_color_same_shape: 44,550
    - same_color_different_shape: 90,000
    - different_color_same_shape: 90,000
    - different_color_different_shape: 180,000
16. color/shape aggregateが元カテゴリの集合結合と完全一致する。
17. standardized distanceのmean/stdがTrain latentだけから計算される。
18. initial/finalがそれぞれ自身のTrain統計を使用する。
19. near-zero次元と使用次元が記録される。
20. bootstrapが承認済みsample単位アルゴリズムを使い、pair直接bootstrapを行わない。
21. 同一`analysis_seed`でbootstrap CIが一致する。
22. Pixel baselineの標準化、C選択、Test利用がTrain/Validation/Test規則に従う。
23. SUCCESS判定を純粋関数として実装し、閾値ちょうど、4/5、3/5、正負ゼロ、属性ORの境界ケースをテストする。
24. INCONCLUSIVE / NO_EVIDENCEについて、承認後の全分岐をtable-driven testで網羅する。
25. 正式5 run集合、各runのgit commit・全seed・設定・指標をExperiment-level成果物から追跡できる。
26. 必須成果物から線形probe、距離、bootstrap、最終判定を再計算できる。
27. 失敗runが保存され、既存runが上書きされない。
