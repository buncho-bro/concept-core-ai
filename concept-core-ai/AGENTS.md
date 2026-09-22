# AGENTS.md

# Project

このリポジトリは「概念核」に基づくAIについて研究するための
実験プロジェクトである。

# Roles

## Human

研究上の最終決定を行う。

以下はHumanの承認なしに変更してはならない。

- 研究仮説
- 実験目的
- 成功条件
- データセット条件
- モデルの学習目的
- 評価方法
- 実験結果の科学的解釈

## ChatGPT

Humanとの議論を通して、

- 仮説整理
- 実験設計
- Codexからの提案の検討
- 実験結果の解釈

を支援する。

ChatGPTとの会話そのものは正式な仕様ではない。
正式な決定はリポジトリ内の文書へ反映する。

## Codex

Codexは主に、

- 実装
- テスト
- 実験実行
- データ収集
- 結果整理

を担当する。

研究条件を独断で変更してはならない。

# Research Rules

- 概念をモデルへ直接教えない。
- 評価ラベルをAutoencoderの学習に使用しない。
- 仮説に反する結果も保存する。
- 失敗したrunを削除しない。
- 実験結果と解釈を区別する。
- 再現性を維持する。

# Specification Rules

実験仕様は

experiments/<experiment_id>/spec.md

を唯一の正式な仕様とする。

仕様に曖昧さがある場合、Codexは勝手に研究条件を決定しない。

# Proposal Rules

Codexが仕様変更を提案することは許可する。

ただし、

PROPOSED

として提示し、人間による承認前に実装してはならない。

# Workflow

REVIEW
↓
DECISION
↓
IMPLEMENT
↓
VERIFY
↓
RUN
↓
ANALYZE

の順番で作業する。