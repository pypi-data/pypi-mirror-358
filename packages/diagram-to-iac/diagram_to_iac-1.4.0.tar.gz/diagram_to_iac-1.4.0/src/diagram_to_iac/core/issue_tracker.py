import json
from pathlib import Path
from typing import Dict, Optional

class IssueTracker:
    """Simple persistent tracker for GitHub issues keyed by repo and error type."""

    def __init__(self, file_path: Optional[str] = None):
        if file_path is None:
            base_dir = Path(__file__).resolve().parents[3]
            file_path = base_dir / "data" / "db" / "issue_tracker.json"
        self.file_path = Path(file_path)
        self._table: Dict[str, Dict[str, int]] = {}
        self._load()

    def _load(self) -> None:
        if self.file_path.exists():
            try:
                with open(self.file_path, "r") as f:
                    self._table = json.load(f)
            except Exception:
                self._table = {}
        else:
            self.file_path.parent.mkdir(parents=True, exist_ok=True)
            self._table = {}

    def _save(self) -> None:
        try:
            self.file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.file_path, "w") as f:
                json.dump(self._table, f, indent=2)
        except Exception:
            pass

    def get_issue(self, repo_url: str, error_type: str) -> Optional[int]:
        return self._table.get(repo_url, {}).get(error_type)

    def record_issue(self, repo_url: str, error_type: str, issue_id: int) -> None:
        repo_map = self._table.setdefault(repo_url, {})
        repo_map[error_type] = issue_id
        self._save()

    def clear(self) -> None:
        self._table = {}
        if self.file_path.exists():
            try:
                self.file_path.unlink()
            except Exception:
                pass
