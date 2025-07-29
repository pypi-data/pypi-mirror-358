"""
Core foundation modules for CUE-AI Architect framework.
"""

try:
    from .foundations.pre_metric_substrate import PreMetricSubstrate
except ImportError:
    PreMetricSubstrate = None

__all__ = [
    "PreMetricSubstrate"
]
