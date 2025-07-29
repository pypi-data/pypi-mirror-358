import pandas as pd
from .detectors import psi_score
from .hooks import run_hook


class DriftResult:
    def __init__(self, drift_detected: bool, psi: dict, threshold: float):
        self.drift = drift_detected
        self.psi = psi
        self.threshold = threshold

    def on_drift(self, func):
        if self.drift:
            run_hook(func)
        return self


class DriftMonitor:
    def __init__(self, reference: pd.DataFrame):
        self.reference = reference

    def watch(self, live_data: pd.DataFrame, threshold: float = 0.1):
        psi = psi_score(self.reference, live_data)
        drift = any(score > threshold for score in psi.values())
        return DriftResult(drift, psi, threshold)
