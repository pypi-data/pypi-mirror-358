import pandas as pd
import numpy as np


def psi_score(reference: pd.DataFrame, live: pd.DataFrame, bins=10) -> dict:
    psi_values = {}
    common_cols = set(reference.columns).intersection(set(live.columns))

    for col in common_cols:
        try:
            ref_col = reference[col].dropna()
            live_col = live[col].dropna()

            # Skip if no data
            if ref_col.empty or live_col.empty:
                print(f"[watchdog] Skipping '{col}' — empty reference or live data.")
                psi_values[col] = -1
                continue

            # Numeric column handling
            if np.issubdtype(ref_col.dtype, np.number):
                combined = pd.concat([ref_col, live_col])
                bins_edges = np.histogram_bin_edges(combined, bins=bins)

                ref_counts, _ = np.histogram(ref_col, bins=bins_edges)
                live_counts, _ = np.histogram(live_col, bins=bins_edges)

                ref_sum = ref_counts.sum()
                live_sum = live_counts.sum()

                if ref_sum == 0 or live_sum == 0:
                    print(f"[watchdog] Skipping '{col}' — empty bins after histogram.")
                    psi_values[col] = -1
                    continue

                ref_dist = ref_counts / ref_sum
                live_dist = live_counts / live_sum

            # Categorical column handling
            else:
                ref_dist = ref_col.value_counts(normalize=True)
                live_dist = live_col.value_counts(normalize=True)

                # Align indices
                all_categories = set(ref_dist.index).union(set(live_dist.index))
                ref_dist = ref_dist.reindex(all_categories, fill_value=1e-6)
                live_dist = live_dist.reindex(all_categories, fill_value=1e-6)

            # Final PSI calc (for both numeric and categorical)
            ref_dist = np.where(ref_dist == 0, 1e-6, ref_dist)
            live_dist = np.where(live_dist == 0, 1e-6, live_dist)

            psi = np.sum((ref_dist - live_dist) * np.log(ref_dist / live_dist))
            psi_values[col] = round(psi, 4)

        except Exception as e:
            print(f"[watchdog] Error in '{col}': {e}")
            psi_values[col] = -1  # fallback score

    return psi_values
