# CONFLICTS

## C-v3-01 — 旧APPROVED Decisionの「有効run」条件

APPROVEDなDEC-NB01「5 run未満の場合」は「正式な有効runが5件」未満なら`NOT_EVALUATED`とする。一方、現行`spec.md` §18.7/§21.xは同一commitの**non-INVALID** runが正式5 seed分あれば先へ進むと定め、`EXPERIMENTAL_FAILURE`を含む5 runは主要指標欠損時に`INCONCLUSIVE`とする。`VALID`というexecution statusが新たに定義されたため、4 VALID＋1 EXPERIMENTAL_FAILUREは旧文言を厳密に読むと`NOT_EVALUATED`、現行specでは`INCONCLUSIVE`になる。

優先順位では現行`spec.md`が上位なので実装時の判定は`INCONCLUSIVE`と一意に決まる。旧DEC-NB01の該当文をSUPERSEDED等で整理することを推奨するが、この記録上の矛盾だけではIMPLEMENTのBLOCKERとしない。新しいAPPROVEDなDEC-NB-v2-01は現行specと一致する。
