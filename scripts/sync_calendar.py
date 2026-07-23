import argparse
import os
import sys
from datetime import date, datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from application.task_management.daily_action_service import DailyActionService  # noqa: E402
from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402

from infrastructure.calendar.google_calendar_gateway import GoogleCalendarGateway  # noqa: E402
from infrastructure.task_management.task_repository import SqlTaskRepository  # noqa: E402


def main():
    parser = argparse.ArgumentParser(description="Sync Calendar from Task Registry.")
    parser.add_argument("--date", type=str, help="Target date in YYYY-MM-DD format (default: today)")
    args = parser.parse_args()

    target_date = date.today()
    if args.date:
        target_date = datetime.strptime(args.date, "%Y-%m-%d").date()

    print(f"Synchronizing calendar for {target_date}...")

    try:
        db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "you_inc_ops.db"))
        engine = create_engine(f"sqlite:///{db_path}")
        SessionLocal = sessionmaker(bind=engine)

        with SessionLocal() as session:
            task_repo = SqlTaskRepository(session)
            calendar_repo = GoogleCalendarGateway()

            service = DailyActionService(task_repo=task_repo, calendar_repo=calendar_repo)

            # 計画とカレンダー同期の実行
            service.plan_day(target_date=target_date, sync_to_calendar=True)
            print(f"✅ Sync completed for {target_date}.")

    except Exception as e:
        print(f"❌ Failed to sync calendar: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
