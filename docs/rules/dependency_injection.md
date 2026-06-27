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
