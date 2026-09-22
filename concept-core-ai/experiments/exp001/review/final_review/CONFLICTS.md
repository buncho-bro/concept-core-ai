# CONFLICTS

## C-01 — run単位Reportと5-seed判定が両立していない

Section 18は「1回のrunごと」の成果物として最終三値判定を要求しているが、Section 14の判定は5 seedの集約を必要とする。単一runの`report.md`では最終判定できない。

## C-02 — `review/BLOCKERS.md`が更新前の状態を記述している

同文書のB-05はMSE Decisionを「PROPOSEDかつ未決定」と記述しているが、`decisions.md`ではDEC-001がSUPERSEDED、DEC-B05がAPPROVEDである。

## C-03 — `review/CONFLICTS.md`が解消済みの矛盾を現在形で保持している

同文書のC-01〜C-05は、更新済み`spec.md`では概ね解消されている。履歴文書として残す場合はRESOLVED表示が必要である。

review文書は非正規仕様であるため、これ自体が研究条件を上書きするものではない。

DEC-B01〜DEC-B08と更新済み`spec.md`の間には、上記以外の直接的な条件矛盾は確認されなかった。
