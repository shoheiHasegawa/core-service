# DDD Guidelines

- **Domain**: ドメインモデル、エンティティ、値オブジェクト、ドメインイベント。
- **Application**: ユースケースのオーケストレーション。副作用を持たない。
  - **Facade & UseCase パターン**: Application層は、すべての処理を1つのクラスに詰め込む「ファットサービス」を禁止します。外部（APIやCLI等）向けのエントリーポイントとして Facade パターン (`~Service`) を配置し、実際の複雑なビジネスロジックはSRP（単一責任の原則）に基づく個別の `~UseCase` クラスに処理を委譲してください。
- **Infrastructure**: 外部IF（外部API、DB）のAdapter。
