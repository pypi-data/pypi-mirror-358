import pandas as pd
from datetime import datetime
import os


def log_drift_result(psi_scores, drift_status, path):
    timestamp = datetime.now().isoformat()
    row = {
        "timestamp": timestamp,
        "drift": drift_status,
        **psi_scores
    }

    df = pd.DataFrame([row])
    log_dir = os.path.dirname(path)

    if not os.path.exists(log_dir):
        print(f"[watchdog] logs/ directory not found.")
        os.makedirs(log_dir)
        print(f"[watchdog] logs created at {os.path.abspath(log_dir)}")

    if not os.path.exists(path):
        df.to_csv(path, index=False)
    else:
        df.to_csv(path, mode='a', header=False, index=False)
