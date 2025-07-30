# etsi/watchdog/drift/factory.py

from .psi import psi_drift
from .shap_drift import shap_drift


def get_drift_function(algo: str):
    algo = algo.lower()
    if algo == "psi":
        return psi_drift
    elif algo == "shap":
        return shap_drift
    else:
        raise ValueError(f"Unsupported drift algorithm: {algo}")
