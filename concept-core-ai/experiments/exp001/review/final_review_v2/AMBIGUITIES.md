# AMBIGUITIES

- `spec.md` §15.1・§15.5・§15.6: 同じ`analysis_seed`でも復元抽出の乱数列と百分位算出法により報告CIが変わる。NB-v2-02を参照。
- `spec.md` §13.7・§15.6・§16.5・§17.6・§18.3: probe、bootstrap、Pixel baselineのFAILEDとrun status、5 run集約との関係が未定で、最終状態が変わる。NB-v2-01を参照。

乱数生成器・shuffleの実装選択による個別画像やsplitの違いは、承認された分布と固定commit・環境・seedに基づく再現性を守り、実装とライブラリ版を記録する限り、追加研究判断を要する曖昧さとは判定しなかった。ただしbootstrapは同一入力から算出する正式なCIそのものの差であるため別扱いとした。16 subpixel平均後に整数へ再量子化する処理は正規仕様にないため、認められた別解とは扱わない。
