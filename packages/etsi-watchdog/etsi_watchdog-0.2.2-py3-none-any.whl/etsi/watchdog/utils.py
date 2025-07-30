import pandas as pd
from datetime import datetime
from pathlib import Path
import json
import warnings

def log_drift_result(psi_scores, drift_status, path: str):
    """
    Appends drift results (timestamp + PSI scores) to a CSV or JSON log file.
    """
    # Type safety
    if not isinstance(psi_scores, dict):
        raise TypeError("psi_scores must be a dict")

    timestamp = datetime.now().isoformat()
    row = {
        "timestamp": timestamp,
        "drift": drift_status,
        **psi_scores
    }

    path_obj = Path(path)
    path_obj.parent.mkdir(parents=True, exist_ok=True)

    # CSV logging
    if path_obj.suffix == ".csv":
        df = pd.DataFrame([row])
        if not path_obj.exists():
            df.to_csv(path_obj, index=False)
        else:
            df.to_csv(path_obj, mode='a', header=False, index=False)
        print(f"[etsi-watchdog] Logged drift event to {path_obj.resolve()}")

    # JSON logging (append style)
    elif path_obj.suffix == ".json":
        if path_obj.exists():
            try:
                existing = json.loads(path_obj.read_text())
                if not isinstance(existing, list):
                    existing = []
            except json.JSONDecodeError:
                existing = []
        else:
            existing = []

        existing.append(row)
        path_obj.write_text(json.dumps(existing, indent=2))
        print(f"[etsi-watchdog] Logged drift event to {path_obj.resolve()}")

    else:
        warnings.warn(f"[etsi-watchdog] Unsupported log format: {path_obj.suffix}. Use .csv or .json")
