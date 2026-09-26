# BLOCKER STATUS

| 項目 | 状態 | 根拠 |
| --- | --- | --- |
| REV-002-01 | RESOLVED | `aggregate` は path 群を受けず baseline だけを受ける。`aggregate_baseline` は baseline の canonical registration からのみ artifact を解決し、retry は audit 表示のみ。first-registration-wins と INVALID/EXPERIMENTAL_FAILURE canonical の非置換も確認。 |
| REV-002-02 | OPEN | frozen performance JSON は run 設定へ束縛されるが、`Performance.apply()` が OMP/MKL environment variables を Python 起動後に上書きするだけで、起動時の native runtime 設定が manifest と一致することを検証しない。`NEW_BLOCKERS.md` を参照。 |
| A-002-01 | RESOLVED_BY_HD-002-01 | HD-002-01 と §50A が first-registration-wins、retry 非置換、new baseline の必要性を明文化し、実装も canonical selection を固定する。後継 baseline の Human authorization の記録・検証不足は REV-002-03 として別に扱う。 |
