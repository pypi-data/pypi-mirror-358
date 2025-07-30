import pandas as pd
from .detectors import psi_score
from .utils import log_drift_result
from .hooks import DriftHook


class DriftResult:
    def __init__(self, psi_scores, threshold, log_path=None):
        self.psi = psi_scores
        self.drift = any(score > threshold for score in psi_scores.values())
        self.hook = DriftHook()
        self.log_path = log_path

        if log_path:
            log_drift_result(psi_scores, self.drift, log_path)

    def on_drift(self, action):
        if self.drift:
            self.hook.trigger(action)
        return self

    def top_features(self, n=3):
        return sorted(self.psi.items(), key=lambda x: x[1], reverse=True)[:n]


class DriftMonitor:
    def __init__(self, reference: pd.DataFrame):
        self.reference = reference
        self.log_path = None

    def watch(self, live: pd.DataFrame, threshold: float = 0.2):
        scores = psi_score(self.reference, live)
        return DriftResult(scores, threshold, log_path=self.log_path)

    def watch_rolling(self, live: pd.DataFrame, window=7, freq="D", threshold: float = 0.2):
        if not isinstance(live.index, pd.DatetimeIndex):
            raise ValueError("Live data must have a DatetimeIndex for rolling drift.")

        drift_results = []
        for date, df in live.groupby(pd.Grouper(freq=freq)):
            if len(df) >= window:
                result = self.watch(df.tail(window), threshold=threshold)
                drift_results.append((date, result))
        return drift_results

    def enable_logging(self, path: str):
        self.log_path = path
