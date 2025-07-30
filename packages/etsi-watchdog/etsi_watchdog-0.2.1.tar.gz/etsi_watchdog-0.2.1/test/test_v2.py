import pandas as pd
from etsi.watchdog import DriftMonitor

# Reference dataset
ref = pd.DataFrame({
    "feature1": [1, 2, 3, 4, 5],
    "feature2": [100, 102, 101, 98, 99],
    "category": ["A", "B", "A", "C", "B"]
})

# Simulate time-stamped live data
dates = pd.date_range("2024-01-01", periods=15)
live = pd.DataFrame({
    "feature1": [10, 12, 12, 13, 14, 15, 16, 18, 20, 21, 22, 24, 25, 27, 28],
    "feature2": [180 + i for i in range(15)],
    "category": ["C", "C", "D", "D", "D", "E", "E", "F", "G", "H", "H", "H", "I", "J", "J"]
}, index=dates)

monitor = DriftMonitor(reference=ref)
monitor.enable_logging("logs/drift_log.csv")

# Basic watch
result = monitor.watch(live.tail(5))
print("Latest PSI:", result.psi)
print("Top features:", result.top_features(2))
result.on_drift(lambda: print("Drift detected."))

# Rolling drift over days
rolling = monitor.watch_rolling(live, window=5)
for dt, res in rolling:
    print(f"{dt.date()} | Drift: {res.drift} | Top: {res.top_features(2)}")
