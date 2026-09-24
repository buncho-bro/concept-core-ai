# NEW_BLOCKERS

## NB-002-01 — Balanced reconstruction loss の集計単位

§12 の `mean squared error over foreground/background pixels` は、ミニバッチ全体で各領域の RGB 要素をまとめて平均する方法と、各画像で領域平均を計算して画像間平均する方法の両方を許す。図形面積が画像ごとに違うため、前者では面積によって画像の勾配寄与が変わり、学習済み表現・再構成 gate・SUCCESS 判定が変わり得る。Human は Train loss と §13–15 の評価値について、領域平均と画像・バッチ集計の順序を決定する必要がある。どちらも未承認の選択肢であり、ここでは採用しない。

## NB-002-02 — Seen-only distance bootstrap の標本設計と乱数系列

§23 は Seen Test 600 件の各距離カテゴリに 95% bootstrap CI を必須とする。一方、継承元 Experiment 001 §15 は Test 900 件、各反復 900 件抽出、index `0..899` を定め、Experiment 002 §28–32 は **cross-distance** 用に 600 件と 300 件を順に抽出する。Seen-only CI にどの母集団・反復抽出数・RNG stream／呼び出し順を適用するかは一意でない。600 件から 600 件、600 件から 900 件、cross-distance の抽出を再利用する方法では CI とその再現性が異なり得る。Human は Seen-only CI の標本設計、cross-distance bootstrap との RNG 共有／独立、呼び出し順を決定する必要がある。§24 の Held-out-only distance に CI を要求するかどうかも、その際に明示するとよい。
