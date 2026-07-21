import os
import sys
from datetime import date

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# パスを追加してモジュールをインポート可能にする
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from domain.task_management.recurring_task import RecurringTask
from domain.task_management.task import TaskCategory
from infrastructure.db.models import Base, RecurringTaskModel
from infrastructure.task_management.recurring_task_repository import SqlRecurringTaskRepository

# DB接続設定
DATABASE_URL = "sqlite:///you_inc_ops.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def seed_recurring_tasks():
    # 万が一テーブルが存在しない場合は作成
    Base.metadata.create_all(bind=engine)

    with SessionLocal() as session:
        repo = SqlRecurringTaskRepository(session)

        tasks_to_seed = [
            # 1. 固定時間ブロック（アブソリュートブロック）
            RecurringTask(
                id="rt-fixed-01",
                name="月金 7:00-9:00 の筋トレ",
                rule_type="fixed_time",
                cron_schedule="0 7 * * 1,5",
                start_time="07:00",
                end_time="09:00",
                duration_minutes=120,
                category=TaskCategory.SHOULD,
                valid_from=date(2026, 7, 1),
                valid_until=None,
                day_context="WORKDAY",
            ),
            RecurringTask(
                id="rt-fixed-02",
                name="平日 5:00-7:00 のDeep Work",
                rule_type="fixed_time",
                cron_schedule="0 5 * * *",
                start_time="05:00",
                end_time="07:00",
                duration_minutes=120,
                category=TaskCategory.MUST,
                valid_from=date(2026, 7, 1),
                valid_until=None,
                day_context="ANY",
            ),
            RecurringTask(
                id="rt-fixed-03",
                name="業務時間 (壁ブロック)",
                rule_type="fixed_time",
                cron_schedule="0 9 * * 1-5",
                start_time="09:00",
                end_time="18:00",
                duration_minutes=540,
                category=TaskCategory.MUST,
                valid_from=date(2026, 7, 1),
                valid_until=None,
                day_context="WORKDAY",
            ),
            # 2. 流動的な定期タスク
            RecurringTask(
                id="rt-flex-01",
                name="毎月の目標エビデンス作成",
                rule_type="flexible_date",
                cron_schedule="0 10 1 * *",
                start_time=None,
                end_time=None,
                duration_minutes=60,
                category=TaskCategory.MUST,
                valid_from=date(2026, 7, 1),
                valid_until=None,
                day_context="WORKDAY",
            ),
            RecurringTask(
                id="rt-flex-02",
                name="勤怠入力",
                rule_type="flexible_date",
                cron_schedule="0 18 * * 1-5",
                start_time=None,
                end_time=None,
                duration_minutes=15,
                category=TaskCategory.MUST,
                valid_from=date(2026, 7, 1),
                valid_until=None,
                day_context="WORKDAY",
            ),
            RecurringTask(
                id="rt-flex-03",
                name="企業型DC資産配分変更",
                rule_type="flexible_date",
                cron_schedule="0 10 1 * *",
                start_time=None,
                end_time=None,
                duration_minutes=30,
                category=TaskCategory.SHOULD,
                valid_from=date(2026, 7, 1),
                valid_until=None,
                day_context="WORKDAY",
            ),
            RecurringTask(
                id="rt-flex-04",
                name="ローテーション家事",
                rule_type="flexible_date",
                cron_schedule="0 10 * * 0,6",
                start_time=None,
                end_time=None,
                duration_minutes=60,
                category=TaskCategory.MUST,
                valid_from=date(2026, 7, 1),
                valid_until=None,
                day_context="HOLIDAY",
            ),
            RecurringTask(
                id="rt-flex-05",
                name="ギターの練習",
                rule_type="flexible_date",
                cron_schedule="0 19 * * *",
                start_time=None,
                end_time=None,
                duration_minutes=30,
                category=TaskCategory.WANT,
                valid_from=date(2026, 7, 1),
                valid_until=None,
                day_context="ANY",
            ),
            RecurringTask(
                id="rt-flex-06",
                name="楽天銀行へ引落し分移動",
                rule_type="flexible_date",
                cron_schedule="0 10 25 * *",
                start_time=None,
                end_time=None,
                duration_minutes=15,
                category=TaskCategory.MUST,
                valid_from=date(2026, 7, 1),
                valid_until=None,
                day_context="WORKDAY",
            ),
        ]

        # 冪等性の担保（既存のものはスキップまたは上書き）
        for task in tasks_to_seed:
            existing = session.query(RecurringTaskModel).filter_by(id=task.id).first()
            if not existing:
                repo.save(task)
                print(f"✅ Created: {task.name}")
            else:
                # Update properties if needed, or skip
                print(f"⏩ Skipped (Already exists): {task.name}")

        session.commit()
        print("\n🎉 Seeding of recurring_tasks completed successfully!")


if __name__ == "__main__":
    seed_recurring_tasks()
