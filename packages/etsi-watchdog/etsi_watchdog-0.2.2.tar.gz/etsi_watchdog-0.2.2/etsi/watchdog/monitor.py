# etsi/watchdog/monitor.py

from .drift_check import DriftCheck
from .logger import log_drift
import pandas as pd


class Monitor:
    """
    Monitor — Periodic/rolling drift monitoring.

    Example:
    >>> monitor = Monitor(reference_df)
    >>> monitor.enable_logging("logs/drift.csv")
    >>> monitor.watch(live_df)
    """

    def __init__(self, reference_df):
        self.reference = reference_df
        self.log_path = None

    def enable_logging(self, path: str):
        self.log_path = path

    def watch(self, live_df: pd.DataFrame, features=None, algorithm="psi", threshold=0.2):
        checker = DriftCheck(self.reference, algorithm=algorithm, threshold=threshold)
        features = features or list(self.reference.columns)
        results = checker.run(live_df, features=features)

        for feat, res in results.items():
            if self.log_path:
                log_drift(res, self.log_path, feature=feat)
        return results

    def watch_rolling(self, live_df: pd.DataFrame, window=50, freq="D", features=None, algorithm="psi", threshold=0.2):
        if not isinstance(live_df.index, pd.DatetimeIndex):
            raise ValueError("Live data must have a DatetimeIndex for rolling drift detection.")

        results = []
        for timestamp, group in live_df.groupby(pd.Grouper(freq=freq)):
            if len(group) >= window:
                chunk = group.tail(window)
                result = self.watch(chunk, features=features, algorithm=algorithm, threshold=threshold)
                results.append((timestamp, result))
        return results
