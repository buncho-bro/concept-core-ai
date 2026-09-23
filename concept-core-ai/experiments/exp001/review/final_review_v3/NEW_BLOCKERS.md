# NEW_BLOCKERS

## NB-v3-01 — bootstrap抽出index列の一意性

Humanの追加決定が必要: `analysis_seed` をPCG64の内部状態に変換する規約と、PCG64の出力から`[0,900)`の整数を得る規約を固定する。特定のライブラリ/APIとバージョン、または検証用の最初のindex列を正式に指定する方法でもよい。この文書はどの方法も承認しない。

`spec.md` §15.7とAPPROVEDなDEC-NB-v2-02はPCG64、連続stream、`low=0, high=900, size=900`を指定する。しかしPCG64はbit generatorであり、整数seedからの状態展開と範囲付き整数への変換は別手順である。[NumPyのPCG64文書](https://numpy.org/doc/stable/reference/random/bit_generators/pcg64.html)も、整数seedを`SeedSequence`で内部状態へ変換し、生成した64-bit値を別の`Generator`等で消費すると説明する。同じ`analysis_seed`でも異なる妥当な組合せから別のindex列が生じ、95% CIという科学的結果が変わり得る。§15.6/DEC-NB-v2-02の「同一入力・seedならindex列も同一」という要件を一意に実装できない。

百分位の補間式、欠損反復の除外、950有効反復閾値は解決済みである。
