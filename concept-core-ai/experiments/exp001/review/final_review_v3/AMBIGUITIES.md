# AMBIGUITIES

- `spec.md` §15.7 / DEC-NB-v2-02: PCG64への整数seed投入時の状態展開と、64-bit乱数から`[0,900)`への整数化が未指定。同一Test入力と`analysis_seed`でも復元抽出index列・CIが変わる。詳細は[NEW_BLOCKERS.md](NEW_BLOCKERS.md)のNB-v3-01。

他の指定された失敗ケースについて、Experiment-levelの判定を変える曖昧さは見つからなかった。旧Decisionの文言との競合は[CONFLICTS.md](CONFLICTS.md)に記録し、現行specの優先順位で解決する。
