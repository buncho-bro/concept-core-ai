# CONFLICTS

## C-002-01 — 継承された 900 件 bootstrap と Seen Test 600 件

Experiment 002 §2 は明示的に上書きしない Experiment 001 条件を継承する。一方、Experiment 002 §23 は 600 件の Seen-only distance CI を要求し、§28–32 は cross-distance bootstrap のみを定義する。継承元 Experiment 001 §15.1、§15.8、§15.10 の 900 件 Test と `0..899` index 規則を Seen-only 解析にそのまま適用できない。解消に必要な判断は `NEW_BLOCKERS.md` の NB-002-02 を参照。
