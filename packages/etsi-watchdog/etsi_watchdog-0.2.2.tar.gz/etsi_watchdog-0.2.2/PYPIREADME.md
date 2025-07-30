# etsi-watchdog

**Real-time data drift detection for machine learning pipelines.**

`etsi-watchdog` is a production-ready Python library for drift detection, version comparison, and real-time monitoring of data streams. Designed for ML practitioners, data scientists, and AI engineers who need reliable data quality insights.


## Features
- PSI-based Drift Detection (more algorithms coming)

- Rolling Monitoring with time-frequency windowing

- Version Drift Comparison between model/data snapshots

- Built-in Visualization & JSON Export

- Minimal Dependencies & Fast Performance

- Clear API, suitable for both research and production

---

## Installation

```bash
pip install etsi-watchdog
```

---

## Quickstart


###  Drift Detection
```bash
from etsi.watchdog import DriftCheck
import pandas as pd

ref = pd.read_csv("reference.csv")
live = pd.read_csv("current.csv")

check = DriftCheck(ref)
results = check.run(live, features=["age", "salary"])

for feat, result in results.items():
    print(result.summary())
    result.plot()

```

### Rolling Monitoring
```bash

from etsi.watchdog import Monitor

monitor = Monitor(reference_df=ref)
monitor.enable_logging("logs/rolling_log.csv")

results = monitor.watch_rolling(
    df=live_data_stream,
    window=50,
    freq="D",
    features=["age", "salary"]
)

```


### Drift Comparison (A/B)
```bash
from etsi.watchdog import DriftComparator

check = DriftCheck(ref)
v1 = check.run(live1, features=["age", "salary"])
v2 = check.run(live2, features=["age", "salary"])

comp = DriftComparator(v1, v2)
print(comp.diff())

```



## Contributing

Contributions are welcome. If you have an idea for a drift metric, integration, or improvement, please open an issue or PR on GitHub.




