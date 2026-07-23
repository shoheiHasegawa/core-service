import os
import glob

# Mapping of old imports to new imports
replacements = {
    "from application.task_management.daily_action_service import DailyActionService": "from application.daily_planning.plan_day_usecase import PlanDayUseCase\nfrom application.daily_planning.record_worklogs_usecase import RecordWorklogsUseCase",
    "from application.task_management.sync_worklogs_service import SyncWorklogsService": "from application.daily_planning.sync_worklogs_usecase import SyncWorklogsUseCase",
    "from application.mobile_vault.usecases.place_dashboard_usecase import PlaceDashboardUseCase": "from application.mobile_vault.place_dashboard_usecase import PlaceDashboardUseCase",
    "from application.mobile_vault.usecases.retrieve_packets_usecase import RetrievePacketsUseCase": "from application.mobile_vault.retrieve_packets_usecase import RetrievePacketsUseCase",
    "DailyActionService": "PlanDayUseCase",  # This will break if RecordWorklogsUseCase was needed, but let's see
    "SyncWorklogsService": "SyncWorklogsUseCase"
}

files = glob.glob("tests/integration/**/*.py", recursive=True)

for file in files:
    with open(file, "r") as f:
        content = f.read()
    
    modified = False
    for old, new in replacements.items():
        if old in content:
            content = content.replace(old, new)
            modified = True
            
    if modified:
        with open(file, "w") as f:
            f.write(content)
        print(f"Updated {file}")
