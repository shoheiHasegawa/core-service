# SOLID Principles & Dependency Injection (DI)

`core-service` はオブジェクト指向設計のベストプラクティスである SOLID 原則を厳格に遵守します。
中でも、DI（依存性逆転）は本システムのアーキテクチャの中核を成します。

## 1. SOLID原則の徹底
1. **S (Single Responsibility Principle)**:
   - クラスは単一の責任のみを持つこと。Application層において、全てのユースケースを1つの `~Service` クラスに実装する「ファットサービス」は SRP 違反です。必ず個別の `~UseCase` クラスに処理を委譲してください。
2. **O (Open-Closed Principle)**:
   - 拡張に対して開かれ、修正に対して閉じていること。新しい機能を追記する際に既存のコードを書き換えるのではなく、新しいクラスやルールを追加する（ポリモーフィズム）設計を心がけてください。
3. **L (Liskov Substitution Principle)**:
   - インターフェース（Port）を実装した派生クラス（Adapter）は、利用側が意識することなく完全に置換可能でなければなりません。
4. **I (Interface Segregation Principle)**:
   - クライアントが使用しないメソッドへの依存を強要してはいけません。巨大なインターフェースは避け、`Publisher`, `Reader`, `Receiver` のように細分化されたインターフェース（Port）を使用してください。
5. **D (Dependency Inversion Principle)**:
   - 上位モジュール（Domain/Application）は下位モジュール（Infrastructure）の実装に依存してはならず、抽象（Interface）に依存しなければなりません。

## 2. Dependency Injection (依存性注入) の実践
`core-service` 内では、具象クラスの直接のインスタンス化（`new` や具象クラスの直接呼び出し）を極力排除します。すべては上位レイヤー側（コンテナ）から注入（DI）されなければなりません。

### Constructor Injection
Service や UseCase のコンストラクタ（`__init__`）で、必要なパス情報（Configから分解されたプリミティブ値）や Repository インターフェースを受け取ります。
Application層のクラスが `Config` クラス全体に依存することは避け、必要な属性のみ（例: `save_dir`, `template_path`）を受け取るようにすることで、ISP（インターフェース分離の原則）を遵守します。

```python
class RegisterNoteUseCase:
    def __init__(self, save_dir: str, repository: ISecondBrainGateway):
        self.save_dir = save_dir
        self.repository = repository
```

## 3. Composition Root
依存関係の構築（DIコンテナの組み立て）は、`core-service/src/di/container.py` に集約します。
`core-service` は単独では実行環境（設定ファイルやDB接続情報）を持たないため、利用側（`agent-core` 等）が起動時に環境情報や設定を渡し、コンテナ経由で組み立て済みの Facade（Service）を取得して実行します。

## 4. Naming Conventions (命名規則)
DIを適用する上で、ドメイン層（インターフェース）とインフラ層（実装クラス）の関心事を分離するため、以下の命名規則を厳守してください。

- **Interface (Domain層)**: ドメインの概念を純粋に表す名称を使用します（例: `TaskRepository`, `PacketReceiver`）。C#等に見られるようなインターフェース特有の接頭辞（例: `ITaskRepository`）は禁止です。
- **Implementation (Infrastructure層)**: 必ず「どんな技術を使って実現しているか」を示す接頭辞を冠します（例: `SqlTaskRepository`, `LocalFilePacketReceiver`）。インターフェース名と全く同じ名前にすることは厳禁です。
