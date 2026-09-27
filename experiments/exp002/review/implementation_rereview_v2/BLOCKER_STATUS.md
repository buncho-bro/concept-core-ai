# Prior findings

## REV-002-01 — RESOLVED

PR #7 で、baseline manifest の canonical registration を唯一の入力にして aggregate が解決する構造になった。PR #8 でもその制約は維持され、任意の attempt path を aggregate に渡して正式結果を作る経路は確認されなかった。

## REV-002-02 — OPEN

PR #8 の正式 CLI は child process に OMP/MKL を渡し、`formal_worker` が NumPy / PyTorch 等の import 前に manifest と照合する。これは正規 CLI 経路を改善している。

ただし `exp002.runner.execute_registered_attempt` は import 可能な実行本体であり、fresh-worker 起動または `validate_process_start` の実行を自身で要求しない。呼出元が渡す `process_start_provenance` 辞書を記録し、環境値と辞書の整合だけを確認する。独立の呼出では、同関数を直接呼び、作成済みの登録と整合する値を渡すことで child 起動前検査を経ずに科学的実行へ到達できた。`run_one` は明示的に拒否する一方、この別の公開実行経路は拒否しない。

このため、manifest に記録される「native import 前の検査済み」という事実を、全正式実行経路で保証できない。修正には、実行本体を worker 専用の非公開境界に閉じる、または worker が生成した検証不能な単なる辞書ではない起動証明を必須にし、他の supported entry point が同本体へ到達できないことをテストする必要がある。研究条件の追加決定は不要である。

## REV-002-03 — RESOLVED

後継 baseline の作成には、`experiments/exp002/authorizations/` 配下のコミット済み JSON 承認記録が必須になった。記録は Decision ID、前任 identity/hash、後継 version、理由、自己整合ハッシュ、Git blob と source commit を結合し、freeze・run・aggregate 時に再検証される。単なる自由記述の `reason` だけで後継を正規 baseline とする経路は解消された。
