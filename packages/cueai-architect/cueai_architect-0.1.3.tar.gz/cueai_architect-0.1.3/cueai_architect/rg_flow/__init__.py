"""
RG Flow Mechanics modules for CUE-AI Architect framework.
"""

try:
    from .mechanics.rg_flow_integrator import RGFlowIntegrator
except ImportError:
    RGFlowIntegrator = None

__all__ = [
    "RGFlowIntegrator"
]
