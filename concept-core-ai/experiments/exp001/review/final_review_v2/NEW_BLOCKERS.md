# NEW_BLOCKERS

## NB-v2-01 — 評価不能な正式runの状態遷移と集約判定

Humanの追加決定が必要: 5 seedの試行がすべて存在する場合、`EXPERIMENTAL_FAILURE`、probe全C非収束、bootstrapの有効反復950未満、Pixel baseline全C非収束をそれぞれどのrun statusに分類し、どの条件で`INCONCLUSIVE`/`NOT_EVALUATED`を出すか。特に評価不能が1 runあり残り4 runが正常な例を一意にすること。

理由: `spec.md` §17.6は指標欠損を伴う`EXPERIMENTAL_FAILURE`を`INCONCLUSIVE`とし、§18.3は「正式な有効run」が5件未満なら`NOT_EVALUATED`とする。前者を有効runに含めるかが未定なので、同じ結果から異なる最終状態が得られる。probe/bootstrapのFAILEDもrun状態へ写像されない。

## NB-v2-02 — bootstrap CIの乱数列と百分位規約

Humanの追加決定が必要: `analysis_seed`から900件の復元抽出を1000回行う乱数生成規約、および有効反復の2.5/97.5百分位を求める順位・補間規約を固定すること。

理由: `spec.md` §15は再標本化の単位とpair構築を厳密に定義したが、同じseedでも乱数生成器・sample抽出API・百分位の補間法によりCI値が変わる。同一latent・metadata・analysis_seedから同一CIを再現するという§15.6の要件を実装間で一意に満たせない。
