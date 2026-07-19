# Dependency Injection (DI) and# Dependency Injection Rules

`core-service` 内では、具象クラスの直接のインスタンス化（`new` やクラスの直接呼び出し）を極力排除します。
すべては Service-Config パターン によって上位レイヤー側から注入（DI）されなければなりません。

## 実装手順 (Reference Implementation)

### 1. Config DataClass の定義
Application Service と同じモジュール内に、必要な設定項目を型定義した `Config` データクラスを作成します。

```python
# src/application/example/example_service.py
from dataclasses import dataclass

@dataclass
class ExampleConfig:
    api_key: str
    target_path: str
```

### 2. Constructor Injection
Service のコンストラクタ（`__init__`）で、定義した Config と必要な Repository インターフェースを受け取ります。

```python
class ExampleService:
    def __init__(self, config: ExampleConfig, repository: IExampleRepository):
        self.config = config
        self.repository = repository
```

## Composition Root
`core-service` 内にすべての依存関係を組み立てる `main.py` やDIコンテナの設定ファイルは置きません。その責務は上位の実行レイヤー（Composition Root）が担います。

## Naming Conventions (命名規則)
DIを適用する上で、ドメイン層（インターフェース）とインフラ層（実装クラス）の関心事を分離するため、以下の命名規則を厳守してください。

### Interface (Domain層)
インターフェース名は、ドメインの概念を純粋に表す名称を使用します（例: `TaskRepository`, `IssueParser`）。
- **禁止事項**: C#やJavaに見られるようなインターフェース特有の接頭辞（例: `ITaskRepository`）を付与してはなりません。

### Implementation (Infrastructure層)
実装クラスは、必ず「どんな技術を使って実現しているか」を示す接頭辞を冠します（例: `SqlTaskRepository`, `LocalFileMobileVaultRepository`）。
- **禁止事項**: インターフェース名と全く同じ名前（例: `TaskRepository`）にしてはなりません。同じ名前にすると、インフラ層のコード内で `import TaskRepository as DomainTaskRepository` のようなエイリアスが必要になり、コードが極めて不格好になります。
