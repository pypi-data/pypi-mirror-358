# etsi/watchdog/hooks.py

from typing import Callable, List


class DriftHook:
    """
    A simple hook system to attach actions when drift is detected or logs are generated.
    Example use cases:
      - Send Slack alerts
      - Push metadata to MLflow
      - Save HTML/Markdown reports
    """

    def __init__(self):
        self._on_drift_actions: List[Callable] = []
        self._on_log_actions: List[Callable] = []

    def register_on_drift(self, func: Callable):
        """Register a callback to run when drift is detected."""
        self._on_drift_actions.append(func)

    def register_on_log(self, func: Callable):
        """Register a callback to run after logging/report generation."""
        self._on_log_actions.append(func)

    def trigger_on_drift(self):
        for action in self._on_drift_actions:
            self._safe_trigger(action)

    def trigger_on_log(self):
        for action in self._on_log_actions:
            self._safe_trigger(action)

    @staticmethod
    def _safe_trigger(action: Callable):
        try:
            action()
        except Exception as e:
            print(f"[etsi-watchdog] Error in hook action: {e}")
