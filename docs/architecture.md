# Architecture (Core Engineering Philosophy)

`core-service` は、You_Incシステムにおけるステートレスで堅牢なドメインロジック/APIを提供する心臓部である。
本リポジトリの開発・保守は、以下の**「5大原則」**を Single Source of Truth (SSOT) として厳格に準拠して行われる。

## 1. DDD (Domain-Driven Design)
レイヤードアーキテクチャを採用し、ビジネスドメインをインフラから完全に隔離する。
ユビキタス言語をコードに直接反映させ、技術的制約をドメインモデルに持ち込まない。
👉 **詳細**: [DDD Guidelines](rules/ddd_guidelines.md)

## 2. SOLID原則 & 依存性逆転 (DI)
単一責任の原則 (SRP) と依存性逆転の原則 (DIP) を中心に据える。
本レイヤーは自身の振る舞いを決定する設定（Config）やパス情報を外部から受け取り、環境依存を排除する（Service-Config パターン）。
オーケストレーションや実行トリガーは上位レイヤー（`agent-core`）の責務とする。
👉 **詳細**: [Dependency Injection](rules/dependency_injection.md)

## 3. SDD (Specification Driven Development)
コーディングを行う前に、必ず `src/application/*/spec.md` を起点としてシナリオ（要求仕様）を明文化する。
仕様のトレーサビリティを確保するため、テストのDocStringには必ずシナリオIDを付与する。

## 4. TDD (Test-Driven Development)
外部インフラへの結合（Integration Test）を先行して固め、インナーループ（Unit Test）でドメインの純度を担保する Outside-in TDD を標準プロトコルとする。
👉 **詳細 (SDD/TDD)**: [Testing Strategy](rules/testing_strategy.md)

## 5. Context Engineering (LLM-Native Architecture)
Agentic OS環境において、AIエージェントのパフォーマンスを引き出し、ハルシネーションを防ぐための物理的なコンテキスト設計（ファイル分割と凝集）のトレードオフを最適化する。
👉 **詳細**: [Context Engineering](rules/context_engineering.md)

---

### レビューおよび品質保証
上記5大原則が遵守されているかを検証するためのゲートウェイとして、自動Linter (`scripts/validate_sdd.py`) およびレビュープロセスが存在する。
👉 **レビュー基準**: [Review Process](review.md)
