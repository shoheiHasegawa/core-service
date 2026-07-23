"""[SCENARIO-00] Integration Test Helpers

このモジュールは、`tests/integration/` 配下の結合テストで共通して使用される
`agent-core` のDIコンテナ代役（IntegrationTestContext）や、
テストデータ生成用ビルダー（TestDataBuilder）を提供します。
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from application.task_operations.refine_task_usecase import RefineTaskUseCase
from application.task_operations.register_task_usecase import RegisterTaskUseCase
from application.task_operations.task_operations_service import TaskOperationsService
from infrastructure.db.models import Base
from infrastructure.task_management.task_repository import SqlTaskRepository


class IntegrationTestContext:
    """
    結合テスト用の実行環境コンテキスト。
    インメモリSQLiteデータベースを作成し、毎テスト後にロールバックまたはスキーマ再作成を行うことで
    State Leakage（状態汚染）を防ぎます。
    """

    def __init__(self):
        self.engine = create_engine("sqlite:///:memory:", echo=False)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()

        # Repositories
        self.task_repo = SqlTaskRepository(self.session)

        # Services
        register_task_uc = RegisterTaskUseCase(self.task_repo)
        refine_task_uc = RefineTaskUseCase(self.task_repo)
        self.task_operations_service = TaskOperationsService(register_task_uc, refine_task_uc)

    def teardown(self):
        self.session.rollback()
        self.session.close()
        Base.metadata.drop_all(self.engine)
        self.engine.dispose()


@pytest.fixture
def test_context():
    context = IntegrationTestContext()
    yield context
    context.teardown()


class TestDataBuilder:
    """テストデータを生成するビルダー"""

    pass
