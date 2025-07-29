"""
AI Integration modules for CUE-AI Architect framework.
"""

try:
    from .integration.consciousness_transformer import ConsciousnessTransformer
except ImportError:
    ConsciousnessTransformer = None

__all__ = [
    "ConsciousnessTransformer"
]
