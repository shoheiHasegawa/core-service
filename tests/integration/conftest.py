"""[SCENARIO-00] Integration Test Helpers

このモジュールは、`tests/integration/` 配下の結合テストで共通して使用される
`agent-core` のDIコンテナ代役（IntegrationTestContext）や、
テストデータ生成用ビルダー（TestDataBuilder）を提供します。
"""


import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from application.task_management.task_management_service import TaskManagementService
from infrastructure.db.models import Base
from infrastructure.task_management.task_repository import TaskRepository


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
        self.task_repo = TaskRepository(self.session)
        # TODO: Other repositories like BriefingRepository, ScheduleGateway, WorklogRepository

        # Services
        # self.daily_action_service = DailyActionService(...)
        self.task_management_service = TaskManagementService(self.task_repo)

    def teardown(self):
        self.session.rollback()
        self.session.close()
        Base.metadata.drop_all(self.engine)

@pytest.fixture
def test_context():
    context = IntegrationTestContext()
    yield context
    context.teardown()

class TestDataBuilder:
    """テストデータを生成するビルダー"""
    pass
