# Experiment 001 Decisions

## DEC-001 Reconstruction Loss

Status: PROPOSED

Question:

Autoencoderの再構成損失として何を使用するか。

Candidates:

- MSE
- BCE
- L1

Proposal:

MSE

Reason:

RGB画像を0〜1の連続値として扱う単純なbaselineとして
実装が容易である。

Decision:

未決定