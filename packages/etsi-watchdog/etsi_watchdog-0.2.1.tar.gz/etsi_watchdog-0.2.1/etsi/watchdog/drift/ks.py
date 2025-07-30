from scipy.stats import ks_2samp
from .base import DriftResult
import warnings

def ks_drift(reference_df, current_df, feature, threshold=0.2) -> DriftResult:
    ref = reference_df[feature].dropna().values
    cur = current_df[feature].dropna().values

    if len(cur) < 50:
        warnings.warn(f"[etsi-watchdog] Feature '{feature}' has few samples (<50): {len(cur)}", stacklevel=2)

    stat, pval = ks_2samp(ref, cur)

    return DriftResult(
        method="ks",
        score=1 - pval,
        threshold=threshold,
        sample_size=len(cur),
        details={
            "ks_statistic": float(stat),
            "p_value": float(pval)
        }
    )
