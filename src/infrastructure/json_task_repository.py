import json
import logging
from datetime import date
from pathlib import Path
from typing import List

from domain.action_pipeline.repository import ITaskRepository
from domain.action_pipeline.task import EnergyLevel, Task, TaskCategory, TaskStatus

logger = logging.getLogger(__name__)


class JsonTaskRepository(ITaskRepository):
    def __init__(self, registry_dir: Path):
        self.registry_dir = registry_dir
        if not self.registry_dir.exists():
            self.registry_dir.mkdir(parents=True)

    def get_ready_tasks_for_date(self, target_date: date) -> List[Task]:
        tasks = []
        for file_path in self.registry_dir.glob("*.json"):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)

                task_date = None
                if data.get("target_date"):
                    task_date = date.fromisoformat(data["target_date"])

                task_deadline = None
                if data.get("deadline"):
                    task_deadline = date.fromisoformat(data["deadline"])

                task = Task(
                    id=data["id"],
                    title=data["title"],
                    category=TaskCategory(data["category"]),
                    energy_level=EnergyLevel(data["energy_level"]),
                    estimated_minutes=data["estimated_minutes"],
                    status=TaskStatus(data.get("status", TaskStatus.TODO.value)),
                    actual_minutes=data.get("actual_minutes", 0),
                    deadline=task_deadline,
                    target_date=task_date,
                    dependencies=data.get("dependencies", []),
                )
                tasks.append(task)
            except (json.JSONDecodeError, KeyError, ValueError) as e:
                logger.warning("Failed to parse %s: %s. Skipping.", file_path.name, e)
                continue

        # Filter purely by target_date and incomplete status.
        # Domain logic (like sliding past tasks) should be handled in the Domain/Application layer.
        return [t for t in tasks if t.status != TaskStatus.COMPLETED and t.target_date == target_date]

    def save_tasks(self, tasks: List[Task]) -> None:
        for task in tasks:
            file_path = self.registry_dir / f"{task.id}.json"

            data = {
                "id": task.id,
                "title": task.title,
                "category": task.category.value,
                "energy_level": task.energy_level.value,
                "estimated_minutes": task.estimated_minutes,
                "status": task.status.value,
                "actual_minutes": task.actual_minutes,
                "deadline": task.deadline.isoformat() if task.deadline else None,
                "target_date": task.target_date.isoformat() if task.target_date else None,
                "dependencies": task.dependencies,
            }

            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
