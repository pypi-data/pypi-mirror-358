# etsi/watchdog/__init__.py

"""
etsi.watchdog — Lightweight Drift Monitoring

Exposes:
- DriftCheck: core drift checker
- Monitor: rolling drift monitor
- DriftComparator: compare two drift runs
- DriftResult: result object with summary, plot, and JSON support
"""

from .drift_check import DriftCheck
from .monitor import Monitor
from .compare import DriftComparator
from .drift.base import DriftResult

__all__ = [
    "DriftCheck",
    "Monitor",
    "DriftComparator",
    "DriftResult",
]
