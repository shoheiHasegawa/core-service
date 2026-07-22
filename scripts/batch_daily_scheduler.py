#!/usr/bin/env python3
"""
毎朝自動実行されるバッチスクリプト。
Task Registry からタスクを読み込み、スケジュールを計算し、Google Calendarへ同期する。
"""

import os
import sys
from datetime import date

# パス追加
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))


def main():
    print("デイリースケジューラーのバッチ処理を開始します...")
    today = date.today()

    try:
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker

        from application.task_management.daily_action_service import DailyActionService
        from infrastructure.calendar.google_calendar_gateway import GoogleCalendarGateway
        from infrastructure.task_management.task_repository import SqlTaskRepository

        # NOTE: 実際のパスに合わせて要修正
        db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "you_inc_ops.db"))
        engine = create_engine(f"sqlite:///{db_path}")
        SessionLocal = sessionmaker(bind=engine)

        with SessionLocal() as session:
            task_repo = SqlTaskRepository(session)
            calendar_repo = GoogleCalendarGateway()

            service = DailyActionService(task_repo=task_repo, calendar_repo=calendar_repo)

            # 計画とカレンダー同期の実行
            briefing = service.plan_day(target_date=today, sync_to_calendar=True)
            print(f"{today} のスケジュール計画およびカレンダー同期が正常に完了しました。")
            print(f"スケジュールされたタスク数: {len(briefing.scheduled_blocks)}")

    except Exception as e:
        print(f"バッチ実行中にエラーが発生しました: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
