# AMBIGUITIES

## A-002-01 — 技術的再試行時の正規 attempt 選定

仕様 §40 は exact formal five-seed set を要求するが、同一 seed の formal attempt が複数保存された場合、どの attempt を正規集合に採用するかの手順は明記しない。現実装は任意の5 path を受け付けるため、結果が変わり得る。REV-002-01 の FIX で仕様の「exact」要件だけから一意に定まらない場合は、Human に決定を求める。レビューでは先着・最新・成功優先等を採用しない。
