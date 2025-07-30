# etsi/watchdog/drift_check.py

from .drift.factory import get_drift_function
from .drift.base import DriftResult


class DriftCheck:
    """
    DriftCheck — Core API to detect drift between reference and current datasets.

    Example:
    >>> check = DriftCheck(reference_df)
    >>> results = check.run(current_df, features=["age", "salary"])
    """

    def __init__(self, reference_df, algorithm="psi", threshold=0.2):
        self.reference = reference_df
        self.algorithm = algorithm
        self.threshold = threshold
        self._func = get_drift_function(algorithm)

    # etsi/watchdog/drift_check.py

    def run(self, current_df, features):
        results = {}
        for feat in features:
            if feat not in self.reference.columns or feat not in current_df.columns:
                print(f"[etsi-watchdog] Skipping '{feat}' — missing in one of the datasets.")
                continue

            result = self._func(
                reference_df=self.reference,
                current_df=current_df,
                feature=feat,
                threshold=self.threshold
            )

            if result is not None:
                results[feat] = result
        return results

