from dataclasses import dataclass
from datetime import date
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from domain.task_management.task import Task

from domain.task_management.task import TaskCategory


@dataclass
class RecurringTask:
    id: str
    name: str
    rule_type: str
    cron_schedule: str
    start_time: Optional[str]
    end_time: Optional[str]
    duration_minutes: int
    category: TaskCategory
    valid_from: Optional[date]
    valid_until: Optional[date]
    day_context: str = "ANY"

    def is_scheduled_on(self, target_date: date, is_holiday: bool = False) -> bool:
        if self.day_context == "WORKDAY" and is_holiday:
            return False
        if self.day_context == "HOLIDAY" and not is_holiday:
            return False

        if self.rule_type != "cron" or not self.cron_schedule:
            return False

        parts = self.cron_schedule.split()
        if len(parts) != 5:
            return False

        dow_part = parts[4]
        if dow_part == "*":
            return True

        # isoweekday: 1=Mon...7=Sun. cron: 0=Sun, 1=Mon...6=Sat
        cron_dow = target_date.isoweekday()
        if cron_dow == 7:
            cron_dow = 0

        allowed_dows = set()
        for p in dow_part.split(","):
            if "-" in p:
                start, end = p.split("-")
                for d in range(int(start), int(end) + 1):
                    allowed_dows.add(d % 7 if d == 7 else d)
            else:
                d = int(p)
                allowed_dows.add(d % 7 if d == 7 else d)

        return cron_dow in allowed_dows or (cron_dow == 0 and 7 in allowed_dows)

    def to_task(self, target_date: date) -> "Task":
        from datetime import datetime

        from domain.task_management.task import Task

        task = Task(
            id=f"{self.id}_{target_date.strftime('%Y%m%d')}",
            title=self.name,
            category=self.category,
            estimated_minutes=self.duration_minutes,
            area_id="00_Recurring",
            target_date=target_date,
        )
        if self.start_time:
            hour, minute = map(int, self.start_time.split(":"))
            task.start_time = datetime.combine(target_date, datetime.min.time().replace(hour=hour, minute=minute))
        if self.end_time:
            hour, minute = map(int, self.end_time.split(":"))
            task.end_time = datetime.combine(target_date, datetime.min.time().replace(hour=hour, minute=minute))

        return task
