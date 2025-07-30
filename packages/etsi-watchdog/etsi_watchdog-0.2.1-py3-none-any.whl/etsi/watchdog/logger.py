import json
import os
from datetime import datetime


def log_drift(result, path, feature=None):
    timestamp = datetime.now().isoformat()

    row = {
        "timestamp": timestamp,
        "feature": feature if feature else "unknown",
        "method": result.method,
        "score": result.score,
        "threshold": result.threshold,
        "drift": result.is_drifted,
        "sample_size": result.sample_size
    }

    # Append to CSV or JSON based on extension
    log_dir = os.path.dirname(path)
    os.makedirs(log_dir, exist_ok=True)

    if path.endswith(".json"):
        if os.path.exists(path):
            with open(path, "r") as f:
                logs = json.load(f)
        else:
            logs = []

        logs.append(row)
        with open(path, "w") as f:
            json.dump(logs, f, indent=2)

    elif path.endswith(".csv"):
        import pandas as pd
        df = pd.DataFrame([row])
        if not os.path.exists(path):
            df.to_csv(path, index=False)
        else:
            df.to_csv(path, mode="a", header=False, index=False)

    print(f"[watchdog] Drift-Result logged for '{row['feature']}' → {path}")
