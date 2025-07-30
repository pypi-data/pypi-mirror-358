# etsi/watchdog/compare.py

class DriftComparator:
    """
    DriftComparator — Compare drift scores between two DriftCheck results.

    Example:
    >>> comp = DriftComparator(results_v1, results_v2)
    >>> deltas = comp.diff()
    """

    def __init__(self, results1, results2):
        self.results1 = results1
        self.results2 = results2

    def diff(self):
        deltas = {}
        for feature in self.results1:
            if feature in self.results2:
                score1 = self.results1[feature].score
                score2 = self.results2[feature].score
                deltas[feature] = score2 - score1
        return deltas

    def report(self):
        print("\n---Drift Comparison Report---")
        for feature in self.diff():
            delta = self.diff()[feature]
            score1 = self.results1[feature].score
            score2 = self.results2[feature].score
            trend = "⬆Up" if delta > 0 else "⬇Down"
            print(f"{feature}: v1={score1:.4f} → v2={score2:.4f} {trend} Δ={delta:+.4f}")
