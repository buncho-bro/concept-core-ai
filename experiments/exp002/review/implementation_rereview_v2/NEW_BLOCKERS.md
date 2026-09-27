# New finding

## REV-002-04 — OPEN: authorization tests do not run on the project Windows environment

`tests/test_exp002_authorization.py` の `git()` helper は `subprocess.run(..., text=True)` に明示的な encoding を指定していない。Windows の既定 cp932 で `git init` の出力を復号すると `UnicodeDecodeError` が起き、`stdout` が `None` になる。その直後の `.strip()` が `AttributeError` となるため、承認記録の10テストは各 assertion に到達しない。

独立実行結果: `10 failed, 241 passed`。失敗はこのファイルの10件のみで、いずれも temporary Git repository の初期化時である。

これは科学的研究条件の未決定ではない。ただし、後継 baseline の Human 承認を強制する実装の必須自動検証が、実行環境で実効的に機能していない。`encoding="utf-8"` を明示する等で helper を環境非依存にし、当該10件を含む全テストを green にするまで VERIFY へ進めない。
