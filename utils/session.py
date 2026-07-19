import time
from collections import defaultdict


class SessionManager:
    def __init__(self):
        self._sessions = {}
        self._stats = {"total_users": 0, "cases_filed": 0, "pdfs_generated": 0}

    def get_or_create(self, user_id: str) -> dict:
        if user_id not in self._sessions:
            self._sessions[user_id] = {
                "user_id": user_id, "stage": "intake",
                "history_text": "", "extracted": {},
                "law_sections": [], "fir_draft": None,
                "created_at": time.time()
            }
            self._stats["total_users"] += 1
        return self._sessions[user_id]

    def save(self, user_id: str, session: dict):
        self._sessions[user_id] = session
        if session.get("stage") == "complete":
            self._stats["cases_filed"] += 1

    def reset(self, user_id: str) -> dict:
        self._sessions[user_id] = {
            "user_id": user_id, "stage": "intake",
            "history_text": "", "extracted": {},
            "law_sections": [], "fir_draft": None,
            "created_at": time.time()
        }
        return self._sessions[user_id]

    def get_stats(self) -> dict:
        stages = defaultdict(int)
        for s in self._sessions.values():
            stages[s.get("stage","intake")] += 1
        return {**self._stats, "active_sessions": len(self._sessions), "stages": dict(stages)}
