"""
CUE-AI Architect: Modular AI Architecture Components

A comprehensive Python package implementing 100 modular AI architecture components
based on the Collective Unified Equation (CUE) Framework by Karl Farah Ambrosius.
"""

__version__ = "0.1.3"
__author__ = "CUE Framework Research Team"
__email__ = "cue-research@example.com"

# Core imports
from .base import CUEConfiguration, CUEBaseModule, CUEGeometricModule, CUESimulationModule
from .utility.cue_application_manager import CUEApplicationManager

# AI Integration imports
try:
    from .ai.integration.consciousness_transformer import ConsciousnessTransformer
except ImportError:
    # Handle optional dependencies gracefully
    ConsciousnessTransformer = None

# Core Foundation imports
try:
    from .core.foundations.pre_metric_substrate import PreMetricSubstrate
except ImportError:
    PreMetricSubstrate = None

# Cognitive Dynamics imports
try:
    from .cognitive.dynamics.consciousness_field_simulator import ConsciousnessFieldSimulator
except ImportError:
    ConsciousnessFieldSimulator = None

# RG Flow imports
try:
    from .rg_flow.mechanics.rg_flow_integrator import RGFlowIntegrator
except ImportError:
    RGFlowIntegrator = None

# Convenience aliases
ApplicationManager = CUEApplicationManager
Configuration = CUEConfiguration

__all__ = [
    # Version info
    "__version__",
    "__author__", 
    "__email__",
    
    # Core classes
    "CUEConfiguration",
    "CUEBaseModule", 
    "CUEGeometricModule",
    "CUESimulationModule",
    "CUEApplicationManager",
    
    # AI Integration
    "ConsciousnessTransformer",
    
    # Core Foundations
    "PreMetricSubstrate",
    
    # Cognitive Dynamics
    "ConsciousnessFieldSimulator",
    
    # RG Flow Mechanics
    "RGFlowIntegrator",
    
    # Aliases
    "ApplicationManager",
    "Configuration",
]

# Package metadata
PACKAGE_INFO = {
    "name": "cueai-architect",
    "version": __version__,
    "description": "Modular AI Architecture Components based on the CUE Framework",
    "author": __author__,
    "email": __email__,
    "url": "https://github.com/cue-framework/cueai-architect",
    "license": "MIT",
    "keywords": [
        "consciousness", "quantum", "neural-networks", 
        "geometric-deep-learning", "renormalization-group",
        "fiber-bundles", "artificial-intelligence", "cue-framework"
    ]
}

def get_version():
    """Get package version."""
    return __version__

def get_package_info():
    """Get complete package information."""
    return PACKAGE_INFO.copy()
