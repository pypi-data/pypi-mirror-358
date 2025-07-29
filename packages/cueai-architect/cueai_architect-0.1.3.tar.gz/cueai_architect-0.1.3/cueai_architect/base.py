"""
Base classes and configuration for CUE-AI Architect framework.

Provides foundational classes that all CUE modules inherit from,
along with configuration management and common utilities.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, Union, List
import torch
import logging
import uuid
from datetime import datetime


@dataclass
class CUEConfiguration:
    """
    Configuration dataclass for CUE framework parameters.
    
    Contains all the fundamental constants and parameters needed
    for consciousness-matter coupling, RG flow dynamics, and
    geometric processing.
    """
    
    # RG Flow parameters
    kappa: float = 1.0                    # Gravitational coupling
    beta_cog: float = 0.5                 # Cognitive coupling strength
    alpha_ent: float = 0.3                # Entanglement parameter
    
    # Consciousness parameters
    consciousness_coupling: float = 0.1   # Consciousness-matter coupling χ
    fiber_bundle_dim: int = 64            # Consciousness fiber dimension
    coherence_threshold: float = 0.7      # Coherence detection threshold
    
    # Numerical parameters
    tolerance: float = 1e-8               # Numerical tolerance
    max_iterations: int = 1000            # Maximum iterations
    
    # System parameters
    device: str = "cpu"                   # Computation device
    log_level: str = "INFO"               # Logging level
    
    # Advanced parameters
    manifold_resolution: int = 64         # Spatial resolution
    time_steps: int = 1000               # Temporal resolution
    
    def __post_init__(self):
        """Validate configuration parameters."""
        if self.consciousness_coupling < 0:
            raise ValueError("Consciousness coupling must be non-negative")
        if self.fiber_bundle_dim <= 0:
            raise ValueError("Fiber bundle dimension must be positive")
        if self.tolerance <= 0:
            raise ValueError("Tolerance must be positive")


class CUEBaseModule(ABC):
    """
    Abstract base class for all CUE framework modules.
    
    Provides common functionality for initialization, computation,
    state management, and logging across all 100 modules.
    """
    
    def __init__(
        self, 
        config: Optional[CUEConfiguration] = None,
        name: Optional[str] = None,
        **kwargs
    ):
        # Configuration
        self.config = config or CUEConfiguration()
        self.name = name or self.__class__.__name__
        self.id = str(uuid.uuid4())
        
        # State management
        self._is_initialized = False
        self._state = {}
        self._computation_history = []
        
        # Device management
        self.device = torch.device(self.config.device)
        
        # Logging setup
        self.logger = self._setup_logger()
        
        # Timing and performance
        self._creation_time = datetime.now()
        self._last_computation_time = None
        
        self.logger.debug(f"Created {self.name} module with ID {self.id[:8]}")
    
    def _setup_logger(self) -> logging.Logger:
        """Set up module-specific logger."""
        logger = logging.getLogger(f"cueai.{self.name}")
        logger.setLevel(getattr(logging, self.config.log_level.upper()))
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                f'%(asctime)s - {self.name} - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    @abstractmethod
    def initialize(self) -> None:
        """Initialize the module. Must be implemented by subclasses."""
        pass
    
    @abstractmethod
    def compute(self, *args, **kwargs) -> Any:
        """Main computation method. Must be implemented by subclasses."""
        pass
    
    def to_device(self, tensor: torch.Tensor) -> torch.Tensor:
        """Move tensor to the configured device."""
        return tensor.to(self.device)
    
    def get_state(self) -> Dict[str, Any]:
        """Get current module state."""
        return {
            "name": self.name,
            "id": self.id,
            "is_initialized": self._is_initialized,
            "device": str(self.device),
            "creation_time": self._creation_time.isoformat(),
            "last_computation": (
                self._last_computation_time.isoformat() 
                if self._last_computation_time else None
            ),
            "state": self._state.copy(),
            "config": self.config.__dict__.copy()
        }
    
    def set_state(self, state: Dict[str, Any]) -> None:
        """Set module state from dictionary."""
        if "state" in state:
            self._state.update(state["state"])
        
        if "config" in state:
            for key, value in state["config"].items():
                if hasattr(self.config, key):
                    setattr(self.config, key, value)
    
    def log_computation(self, operation: str, result: Any) -> None:
        """Log computation for debugging and monitoring."""
        self._last_computation_time = datetime.now()
        self._computation_history.append({
            "operation": operation,
            "timestamp": self._last_computation_time.isoformat(),
            "result_type": type(result).__name__,
            "result_shape": getattr(result, 'shape', None) if hasattr(result, 'shape') else None
        })
        
        # Keep only last 100 computations
        if len(self._computation_history) > 100:
            self._computation_history = self._computation_history[-100:]
    
    def reset(self) -> None:
        """Reset module to uninitialized state."""
        self._is_initialized = False
        self._state.clear()
        self._computation_history.clear()
        self.logger.info(f"Reset {self.name} module")
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}', id='{self.id[:8]}')"


class CUEGeometricModule(CUEBaseModule):
    """
    Base class for geometric processing modules.
    
    Extends CUEBaseModule with geometric-specific functionality
    for manifold processing, curvature computation, etc.
    """
    
    def __init__(
        self, 
        manifold_dim: int = 4,
        config: Optional[CUEConfiguration] = None,
        **kwargs
    ):
        super().__init__(config=config, **kwargs)
        self.manifold_dim = manifold_dim
        
        # Geometric state
        self._metric_tensor = None
        self._connection = None
        self._curvature = None
        
        self.logger.debug(f"Initialized geometric module with {manifold_dim}D manifold")
    
    def compute_metric(self, coordinates: torch.Tensor) -> torch.Tensor:
        """Compute metric tensor at given coordinates."""
        # Default implementation - identity metric (flat space)
        batch_size = coordinates.shape[0] if coordinates.dim() > 1 else 1
        metric = torch.eye(
            self.manifold_dim, 
            device=self.device,
            dtype=coordinates.dtype
        )
        
        if batch_size > 1:
            metric = metric.unsqueeze(0).expand(batch_size, -1, -1)
        
        return metric
    
    def compute_christoffel_symbols(self, metric: torch.Tensor) -> torch.Tensor:
        """Compute Christoffel symbols from metric tensor."""
        # Simplified implementation
        # In practice, this would involve metric derivatives
        dim = metric.shape[-1]
        christoffel = torch.zeros(
            *metric.shape[:-2], dim, dim, dim,
            device=self.device,
            dtype=metric.dtype
        )
        return christoffel
    
    def compute_curvature_tensor(self, christoffel: torch.Tensor) -> torch.Tensor:
        """Compute Riemann curvature tensor."""
        # Simplified implementation
        dim = christoffel.shape[-1]
        curvature = torch.zeros(
            *christoffel.shape[:-3], dim, dim, dim, dim,
            device=self.device,
            dtype=christoffel.dtype
        )
        return curvature


class CUESimulationModule(CUEBaseModule):
    """
    Base class for simulation and dynamics modules.
    
    Provides time evolution, field dynamics, and simulation
    management capabilities.
    """
    
    def __init__(
        self,
        time_steps: int = 1000,
        dt: float = 0.01,
        config: Optional[CUEConfiguration] = None,
        **kwargs
    ):
        super().__init__(config=config, **kwargs)
        self.time_steps = time_steps
        self.dt = dt
        self.current_time = 0.0
        
        # Simulation state
        self._simulation_history = []
        self._is_running = False
        
        self.logger.debug(f"Initialized simulation module: {time_steps} steps, dt={dt}")
    
    def evolve_step(self, state: torch.Tensor, dt: Optional[float] = None) -> torch.Tensor:
        """Evolve system by one time step."""
        # Default implementation - identity evolution
        return state
    
    def run_simulation(
        self, 
        initial_state: torch.Tensor,
        steps: Optional[int] = None
    ) -> List[torch.Tensor]:
        """Run full simulation."""
        steps = steps or self.time_steps
        self._is_running = True
        
        states = [initial_state.clone()]
        current_state = initial_state
        
        try:
            for step in range(steps):
                current_state = self.evolve_step(current_state, self.dt)
                states.append(current_state.clone())
                self.current_time += self.dt
                
                if step % 100 == 0:
                    self.logger.debug(f"Simulation step {step}/{steps}")
                    
        except KeyboardInterrupt:
            self.logger.warning("Simulation interrupted by user")
        finally:
            self._is_running = False
        
        self._simulation_history.append({
            "steps": len(states) - 1,
            "final_time": self.current_time,
            "timestamp": datetime.now().isoformat()
        })
        
        return states
    
    def reset_simulation(self) -> None:
        """Reset simulation state."""
        self.current_time = 0.0
        self._simulation_history.clear()
        self._is_running = False
        self.logger.info("Simulation state reset")


# Utility functions
def create_default_config(**kwargs) -> CUEConfiguration:
    """Create default configuration with optional overrides."""
    return CUEConfiguration(**kwargs)

def validate_tensor_device(tensor: torch.Tensor, expected_device: torch.device) -> bool:
    """Validate tensor is on expected device."""
    return tensor.device == expected_device

def ensure_tensor_device(tensor: torch.Tensor, device: torch.device) -> torch.Tensor:
    """Ensure tensor is on specified device."""
    if tensor.device != device:
        return tensor.to(device)
    return tensor
