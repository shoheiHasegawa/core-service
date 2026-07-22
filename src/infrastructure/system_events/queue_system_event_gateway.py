import subprocess
from datetime import datetime
from pathlib import Path

from domain.system_events.gateway import SystemEventGateway


class QueueSystemEventGateway(SystemEventGateway):
    def __init__(self, queue_dir: Path):
        self.queue_dir = queue_dir

        # 起動時にキューディレクトリが存在しない場合は作成
        self.queue_dir.mkdir(parents=True, exist_ok=True)

    def publish_error(self, job_name: str, error_details: str) -> None:
        """
        システムエラーイベントをキューに発行し、Macの通知センターに通知する。
        Context Engineeringに基づき、処理粒度が明確な命名規則を使用する。
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # 命名規則: error_{job_name}_{timestamp}.md
        packet_name = f"error_{job_name}_{timestamp}.md"
        packet_path = self.queue_dir / packet_name

        # イベントバス（Queue）にエラーパケットを投函
        with open(packet_path, "w", encoding="utf-8") as f:
            f.write(f"# System Error Event: {job_name}\n\n")
            f.write(f"- **Timestamp**: {timestamp}\n")
            f.write(f"- **Job Name**: {job_name}\n\n")
            f.write("## Error Details\n")
            f.write("```text\n")
            f.write(f"{error_details}\n")
            f.write("```\n")

        # Mac ネイティブ通知のトリガー (ベストエフォート)
        try:
            # 汎用的なメッセージを通知
            title = f"Agent-Core Error: {job_name}"
            msg = f"A fatal error occurred. Check queue for {packet_name}"
            subprocess.run(
                [
                    "osascript",
                    "-e",
                    "on run argv",
                    "-e",
                    'display notification (item 1 of argv) with title (item 2 of argv) sound name "Basso"',
                    "-e",
                    "end run",
                    msg,
                    title,
                ],
                check=False,
            )
        except Exception:
            # 通知失敗は無視（メインのイベント発行を阻害しない）
            pass
