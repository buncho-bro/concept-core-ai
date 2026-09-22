# CONFLICTS

## C-01 Test latent のみの保存と線形プローブ学習が両立しない

- Section 11/18.5 は Test データの latent 保存を指定する。
- Section 12 は latent を入力に線形分類器を学習して性能を測る。
- Test latent だけで学習と評価をすると Test が独立評価集合ではなくなる。Train/Validation latent を使うか、別の probe 用分割規則が必要である。

## C-02 Pixel baseline が必須とも任意とも読める

- Section 13 冒頭は「少なくとも以下と比較する」とする。
- 同節の Pixel baseline は「可能であれば」とする。
- 実装完了条件に Pixel baseline を含めるかが一意に決まらない。

## C-03 「再現可能」が成功条件だが、複数 seed は任意に近い

- Section 14 は「再現可能な規則的構造」を成功条件とする。
- 同節は複数 seed を「望ましい」とするだけで、必須数や判定方法を定めていない。
- 単一 seed では seed を越えた再現可能性を検証できない。

## C-04 未学習モデルに同じ解析を要求するが成果物が一組しかない

- Section 13 は未学習 Encoder に「同じ解析」を要求する。
- Section 18 の `latent_vectors.csv`、PCA、`distance_analysis.csv` は状態を区別する命名・schema になっていない。
- `linear_probe_results.json` だけは initial/final 比較を明示しており、他の解析成果物と非対称である。

## C-05 実行中の設定変更と再現性・失敗 run 保存の境界が不明確

- Section 18.1 は実験開始後の設定変更を許容するように読める。
- Section 15/17/19 は失敗 run の保存と再現性を要求する。
- 途中で研究条件を変更した処理を同一 run とみなすか、新しい run とみなすかが決まっていない。
