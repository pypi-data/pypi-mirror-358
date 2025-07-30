# etsi/watchdog/drift/base.py

import json
import matplotlib.pyplot as plt
from dataclasses import dataclass, asdict


@dataclass
class DriftResult:
    method: str
    score: float
    threshold: float
    details: dict
    sample_size: int

    @property
    def is_drifted(self) -> bool:
        return self.score > self.threshold

    def summary(self) -> str:
        status = "[etsi-watchdog] Drift Detected!" if self.is_drifted else "[etsi-watchdog] No Drift"
        return f"[{self.method.upper()}] Drift Score: {self.score:.4f} (threshold: {self.threshold}) — {status}"

    def plot(self):
        if "bins" in self.details and "expected_percents" in self.details:
            bins = self.details["bins"]
            expected = self.details["expected_percents"]
            actual = self.details["actual_percents"]
            width = 0.35
            x = range(len(bins))

            plt.bar(x, expected, width, label='Reference')
            plt.bar([i + width for i in x], actual, width, label='Current')
            plt.xticks([i + width / 2 for i in x], bins, rotation=45)
            plt.ylabel('Percentage')
            plt.title(f"{self.method.upper()} Distribution")
            plt.legend()
            plt.tight_layout()
            plt.show()

    def to_json(self, path=None):
        data = asdict(self)
        if path:
            with open(path, "w") as f:
                json.dump(data, f, indent=2)
            print(f"[etsi-watchdog] DriftResult written to {path}")
        return data
