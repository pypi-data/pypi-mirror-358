import pandas as pd
from etsi.watchdog import DriftMonitor

X_ref = pd.DataFrame({
    "feature1": [1, 2, 2, 3, 4, 5],
    "feature2": [100, 102, 101, 98, 97, 99],
    "category": ["A", "B", "A", "C", "B", "A"]
})

X_live = pd.DataFrame({
    "feature1": [11, 12, 13, 14, 15, 16],
    "feature2": [188, 189, 190, 191, 192, 193],
    "category": ["A", "C", "C", "C", "D", "D"]
})

def alert():
    print("🚨 Drift detected! Take action!")

monitor = DriftMonitor(reference=X_ref)
result = monitor.watch(X_live, threshold=0.2)

print("PSI Scores:", result.psi)
result.on_drift(alert)
