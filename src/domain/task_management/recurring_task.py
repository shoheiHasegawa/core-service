from dataclasses import dataclass
from datetime import date, datetime
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

        if not self.cron_schedule:
            return False

        parts = self.cron_schedule.split()
        if len(parts) != 5:
            return False

        dom_part = parts[2]
        month_part = parts[3]
        dow_part = parts[4]

        # Month check
        if month_part != "*":
            allowed_months = set()
            for p in month_part.split(","):
                if "-" in p:
                    s, e = p.split("-")
                    for m in range(int(s), int(e) + 1):
                        allowed_months.add(m)
                else:
                    allowed_months.add(int(p))
            if target_date.month not in allowed_months:
                return False

        dom_match = True
        if dom_part != "*":
            allowed_doms = set()
            for p in dom_part.split(","):
                if "-" in p:
                    s, e = p.split("-")
                    for d in range(int(s), int(e) + 1):
                        allowed_doms.add(d)
                else:
                    allowed_doms.add(int(p))
            dom_match = target_date.day in allowed_doms

        dow_match = True
        if dow_part != "*":
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

            dow_match = cron_dow in allowed_dows or (cron_dow == 0 and 7 in allowed_dows)

        if dom_part != "*" and dow_part != "*":
            # In standard cron, if both DOM and DOW are restricted, it's an OR condition
            if not (dom_match or dow_match):
                return False
        else:
            if not dom_match:
                return False
            if not dow_match:
                return False

        return True

    def to_task(self, target_date: date) -> "Task":

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
