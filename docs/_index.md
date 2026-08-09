---
# ドキュメント・インデックス (Core Service)
title: "Core Service: Document Index"
---

# Core Service: Document Index

本リポジトリ（`core-service`）は機能実装（バックエンド）の工場であり、ここにあるドキュメントはAgentic OS全体の「3層アーキテクチャ」における **2. Law (ルール)** と **3. Architecture (構造)** に該当します。
最上位の思想（Philosophy）や共通のメタヒューリスティクスについては、`agent-core/docs/_index.md` を参照してください。

## 2. ルール・踏み台 (Law & Heuristics)
機能実装時にAgentが遵守・JITロードすべきドメイン固有のルール群です。

*   [ddd_guidelines.md](./rules/ddd_guidelines.md): ドメイン駆動設計（DDD）におけるエンティティやレイヤー間の厳密な分離ルール。
*   [testing_strategy.md](./rules/testing_strategy.md): 自動テストの戦略、カバレッジ、およびテストダブルの利用ルール。
*   [dependency_injection.md](./rules/dependency_injection.md): 依存性注入の原則とDIコンテナの構成ルール。
*   [error_handling.md](./rules/error_handling.md): ドメイン例外とインフラ例外の分離、エラー伝播のルール。
*   [context_engineering.md](./rules/context_engineering.md): コンテキスト（状態）の注入・管理ルール。

## 3. 構造・設計 (Architecture & Specifications)
本リポジトリの静的な構造や仕様書です。

*   [architecture.md](./architecture.md): システム構成とディレクトリ構造の地図。
*   [review.md](./review.md): レビュー観点とQuality Gateのチェックリスト。
*   `spec/`: 各サービスの機能仕様書（SDD）が格納されるディレクトリ（例: [second_brain_service.md](./spec/second_brain_service.md)）。
