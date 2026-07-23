# DDD Guidelines (Domain-Driven Design)

本リポジトリ (`core-service`) におけるドメイン駆動設計のルールを定義する。
レイヤードアーキテクチャの厳密な分離と、ユビキタス言語の適用を義務付ける。

## 1. 依存の方向（Dependency Rule）
依存関係は常に「外側の層から内側の層（Domain）」へ向かって一方向に流れること。
- `Domain` は他のいかなる層にも依存してはならない。
- `Application` は `Domain` に依存する。
- `Infrastructure` は `Domain` と `Application` に依存する。

## 2. 各層の責務
### 2.1. Domain層 (`src/domain/`)
- ビジネスのコアロジックをカプセル化する。
- **Entity**: 同一性（ID）を持つオブジェクト（例: `Task`）。
- **Value Object**: 属性のみを持つ不変オブジェクト。
- **Domain Event**: 状態変化を通知するイベント（イベント駆動に必要になった場合）。
- **Port (Interface)**: インフラストラクチャ層の技術的詳細を隠蔽するための抽象インターフェース（Repository, Gateway等）。

### 2.2. Application層 (`src/application/`)
- ユースケースをオーケストレーションする。副作用（外部へのDB保存等）の実行順序を管理する。
- **Facade パターン**: Application層は、すべての処理を1つのクラスに詰め込む「ファットサービス」を禁止する。外部向けのエントリーポイントとして Facade パターン (`~Service`) を配置すること。
- **UseCase パターン**: 実際の複雑なビジネスロジックはSRP（単一責任の原則）に基づく個別の `~UseCase` クラスに処理を委譲すること。UseCase自身は状態を持たず、ステートレスに実行される。
- **DTO**: UseCaseへの入出力は、外部層への過度な公開を防ぐためにDTOを用いること。

### 2.3. Infrastructure層 (`src/infrastructure/`)
- データベース、ファイルシステム、外部APIなどの具体的な技術実装を行う。
- Domain層で定義されたPort（インターフェース）を `implements` （PythonではプロトコルやABCの継承）する。
- Domain層のコードにインフラ固有の技術（SQLAlchemy、Requests、boto3など）が混入してはならない。

## 3. ユビキタス言語の徹底
クラス名、変数名、ファイル名には、業務の専門用語（ユビキタス言語）をそのまま使用すること。
プログラミング特有のシステム的な命名（例: `Manager`, `Processor`, `Helper`）は、ユビキタス言語に存在しない限り使用を避ける。
