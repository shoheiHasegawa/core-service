"""[SCENARIO-00] Integration Test Helpers

このモジュールは、`tests/integration/` 配下の結合テストで共通して使用される
`agent-core` のDIコンテナ代役（IntegrationTestContext）や、
テストデータ生成用ビルダー（TestDataBuilder）を提供します。
"""

class IntegrationTestContext:
    """
    agent-core の DI組み立てを模倣するコンテキストクラス。
    各Integrationテストのセットアップで生成され、本番同等の依存配線を保証します。
    """
    def __init__(self):
        # TODO: 実際の結合テスト実装時に、インメモリDB（SQLite）の生成と
        # Repositoryの具象クラスのインスタンス化、Serviceへの注入を実装する。
        pass

class TestDataBuilder:
    """
    テストデータを生成し、DBに事前投入するための基底ビルダー。
    """
    pass
