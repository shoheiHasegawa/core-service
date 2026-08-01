import datetime

import pytest
from integration.conftest import IntegrationTestContext
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from domain.task_management.task import Worklog
from infrastructure.sqlalchemy.task_model import TaskModel
from infrastructure.sqlalchemy.worklog_model import WorklogModel
from infrastructure.sqlalchemy.worklog_repository import SQLAlchemyWorklogRepository


def test_worklog_model_new_columns(test_context: IntegrationTestContext):
    """[TM-PLAN-03]
    WorklogModelに将来の分析のためのカラム（area_id, category, task_type, is_completed）が追加されていることを検証する
    """
    session: Session = test_context.session

    # 存在しないカラムにアクセスすると AttributeError が発生するはず（これでFailを確認）
    worklog = WorklogModel(
        id="test-wl-01",
        task_id="task-1",
        target_date=datetime.date.today(),
        minutes=30,
        area_id="00_Area",
        category="M",
        task_type="ONE_OFF",
        is_completed=True,
    )

    session.add(worklog)
    session.commit()

    saved_wl = session.query(WorklogModel).filter_by(id="test-wl-01").one()
    assert getattr(saved_wl, "area_id", None) == "00_Area"
    assert getattr(saved_wl, "category", None) == "M"
    assert getattr(saved_wl, "task_type", None) == "ONE_OFF"
    assert getattr(saved_wl, "is_completed", None) is True


def test_worklog_model_unique_constraint(test_context: IntegrationTestContext):
    """[TM-PLAN-03]
    WorklogModelにtask_idとtarget_dateの複合UNIQUE制約（冪等性担保）が設定されていることを検証する
    """
    session: Session = test_context.session

    target_date = datetime.date.today()
    wl1 = WorklogModel(id="test-wl-unique-1", task_id="task-unique", target_date=target_date, minutes=30)
    session.add(wl1)
    session.commit()

    wl2 = WorklogModel(id="test-wl-unique-2", task_id="task-unique", target_date=target_date, minutes=45)
    session.add(wl2)

    with pytest.raises(IntegrityError) as exc_info:
        session.commit()
    assert exc_info.value is not None, "UNIQUE constraint should be raised"

    session.rollback()


def test_task_model_energy_level_column(test_context: IntegrationTestContext):
    """[TM-PLAN-03]
    TaskModelにenergy_levelカラムが追加されていることを検証する
    """
    session: Session = test_context.session

    task = TaskModel(
        id="test-task-energy", title="Energy Task", category="M", estimated_minutes=30, energy_level="HIGH"
    )

    session.add(task)
    session.commit()

    saved_task = session.query(TaskModel).filter_by(id="test-task-energy").one()
    assert getattr(saved_task, "energy_level", None) == "HIGH"


def test_worklog_repository_save_restore_new_columns(test_context: IntegrationTestContext):
    """[TM-PLAN-03]
    SqlWorklogRepository（SQLAlchemyWorklogRepository）が、これら新しいカラムを含むWorklogエンティティを正しく保存・復元できることを検証する
    """
    from domain.task_management.task import TaskCategory, TaskType

    repo = SQLAlchemyWorklogRepository(test_context.session)

    target_date = datetime.date.today()
    worklog = Worklog(
        id="test-repo-wl-1",
        task_id="task-repo-1",
        minutes=60,
        target_date=target_date,
        is_completed=True,
        # 以下のプロパティがWorklogドメインにも追加されている前提でテストする。
        # 現在のドメインモデルに無ければここでエラー（Fail）になる。
    )

    # Pythonは動的に属性を追加できるので、強制的に設定してリポジトリの挙動を確認する
    # ドメインモデルが正式に更新された後は通常のコンストラクタ引数になる想定
    worklog.area_id = "00_Dev"
    worklog.category = TaskCategory.MUST
    worklog.task_type = TaskType.ONE_OFF

    repo.save(worklog)

    # 復元
    restored_list = repo.find_by_task_and_date("task-repo-1", target_date)
    assert len(restored_list) == 1

    restored_wl = restored_list[0]
    assert restored_wl.id == "test-repo-wl-1"
    assert getattr(restored_wl, "area_id", None) == "00_Dev"
    assert getattr(restored_wl, "category", None) == TaskCategory.MUST
    assert getattr(restored_wl, "task_type", None) == TaskType.ONE_OFF
    assert getattr(restored_wl, "is_completed", False) is True
