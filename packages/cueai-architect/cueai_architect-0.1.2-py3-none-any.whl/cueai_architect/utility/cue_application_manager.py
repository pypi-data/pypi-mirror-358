"""
CUE Application Manager

Central orchestration tool for integrating and managing all 100 CUE framework modules.
Provides unified interface for consciousness-matter-AI system coordination,
experiment management, and cross-module communication.

Serves as the primary entry point for CUE-AI Architect applications.
"""

from typing import Dict, Any, Optional, List, Union, Type
import torch
import logging
import json
import pickle
from pathlib import Path
from datetime import datetime
import uuid
from contextlib import contextmanager

from cueai_architect.base import CUEBaseModule, CUEConfiguration, CUESimulationModule


class ModuleRegistry:
    """Registry for managing all 100 CUE framework modules."""

    def __init__(self):
        self.modules: Dict[str, CUEBaseModule] = {}
        self.module_categories: Dict[str, List[str]] = {
            "Core_Foundations": [],
            "Cognitive_Dynamics": [],
            "RG_Flow_Mechanics": [],
            "Geometry_Topology": [],
            "Quantum_Conscious_Interface": [],
            "Measurement_Theory": [],
            "Field_Solvers": [],
            "Sectoral_Processors": [],
            "Holographic_Systems": [],
            "Dark_Sector_Dynamics": [],
            "Simulation_Tools": [],
            "AI_Integration": [],
            "Experimental_Interfaces": [],
            "Utility_Components": []
        }

        self.dependencies: Dict[str, List[str]] = {}
        self.initialization_order: List[str] = []

    def register_module(
        self, 
        module: CUEBaseModule, 
        category: str,
        dependencies: Optional[List[str]] = None
    ) -> None:
        """Register a module with the framework."""
        module_name = module.name

        if module_name in self.modules:
            raise ValueError(f"Module {module_name} already registered")

        if category not in self.module_categories:
            raise ValueError(f"Unknown category: {category}")

        self.modules[module_name] = module
        self.module_categories[category].append(module_name)
        self.dependencies[module_name] = dependencies or []

        # Update initialization order
        self._update_initialization_order()

    def get_module(self, name: str) -> CUEBaseModule:
        """Get module by name."""
        if name not in self.modules:
            raise KeyError(f"Module {name} not found")
        return self.modules[name]

    def get_modules_by_category(self, category: str) -> List[CUEBaseModule]:
        """Get all modules in a category."""
        if category not in self.module_categories:
            raise ValueError(f"Unknown category: {category}")

        return [
            self.modules[name] 
            for name in self.module_categories[category]
        ]

    def _update_initialization_order(self) -> None:
        """Update initialization order based on dependencies."""
        # Topological sort for dependency resolution
        visited = set()
        temp_visited = set()
        order = []

        def visit(module_name: str):
            if module_name in temp_visited:
                raise ValueError(f"Circular dependency detected involving {module_name}")
            if module_name in visited:
                return

            temp_visited.add(module_name)
            for dep in self.dependencies.get(module_name, []):
                if dep in self.modules:
                    visit(dep)
            temp_visited.remove(module_name)
            visited.add(module_name)
            order.append(module_name)

        for module_name in self.modules:
            visit(module_name)

        self.initialization_order = order

    def get_status(self) -> Dict[str, Any]:
        """Get registry status summary."""
        return {
            "total_modules": len(self.modules),
            "categories": {
                cat: len(modules) 
                for cat, modules in self.module_categories.items()
            },
            "initialized_modules": [
                name for name, module in self.modules.items()
                if module._is_initialized
            ],
            "dependency_graph": self.dependencies
        }


class ExperimentManager:
    """Manager for CUE framework experiments and simulations."""

    def __init__(self, base_path: Optional[Path] = None):
        self.base_path = base_path or Path("./cue_experiments")
        self.base_path.mkdir(exist_ok=True)

        self.experiments: Dict[str, Dict[str, Any]] = {}
        self.current_experiment: Optional[str] = None

    def create_experiment(
        self,
        name: str,
        description: str = "",
        config: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create new experiment."""
        experiment_id = str(uuid.uuid4())
        experiment_path = self.base_path / f"{name}_{experiment_id[:8]}"
        experiment_path.mkdir(exist_ok=True)

        experiment_data = {
            "id": experiment_id,
            "name": name,
            "description": description,
            "created_at": datetime.now().isoformat(),
            "config": config or {},
            "path": str(experiment_path),
            "results": {},
            "status": "created"
        }

        self.experiments[experiment_id] = experiment_data

        # Save experiment metadata
        with open(experiment_path / "metadata.json", "w") as f:
            json.dump(experiment_data, f, indent=2)

        return experiment_id

    def set_current_experiment(self, experiment_id: str) -> None:
        """Set current active experiment."""
        if experiment_id not in self.experiments:
            raise KeyError(f"Experiment {experiment_id} not found")
        self.current_experiment = experiment_id

    def save_results(
        self, 
        results: Dict[str, Any], 
        experiment_id: Optional[str] = None
    ) -> None:
        """Save experiment results."""
        exp_id = experiment_id or self.current_experiment
        if exp_id is None:
            raise ValueError("No experiment specified")

        if exp_id not in self.experiments:
            raise KeyError(f"Experiment {exp_id} not found")

        experiment = self.experiments[exp_id]
        experiment["results"].update(results)
        experiment["status"] = "completed"

        # Save to file
        results_path = Path(experiment["path"]) / "results.pkl"
        with open(results_path, "wb") as f:
            pickle.dump(results, f)

    def load_experiment(self, experiment_id: str) -> Dict[str, Any]:
        """Load experiment data."""
        if experiment_id not in self.experiments:
            raise KeyError(f"Experiment {experiment_id} not found")

        experiment = self.experiments[experiment_id]
        results_path = Path(experiment["path"]) / "results.pkl"

        if results_path.exists():
            with open(results_path, "rb") as f:
                experiment["results"] = pickle.load(f)

        return experiment


class CUEApplicationManager(CUEBaseModule):
    """
    Central orchestration manager for CUE-AI Architect framework.

    Provides unified interface for:
    - Module registration and dependency management
    - Experiment orchestration and results tracking
    - Cross-module communication and data flow
    - Configuration management and persistence
    - Performance monitoring and diagnostics
    """

    def __init__(
        self,
        config: Optional[CUEConfiguration] = None,
        experiment_base_path: Optional[Path] = None,
        auto_initialize_modules: bool = True,
        **kwargs
    ):
        super().__init__(config=config, name="CUEApplicationManager", **kwargs)

        # Core components
        self.registry = ModuleRegistry()
        self.experiment_manager = ExperimentManager(experiment_base_path)

        # Configuration
        self.auto_initialize_modules = auto_initialize_modules

        # System state
        self.system_state = {
            "consciousness_field": None,
            "rg_flow_state": None,
            "quantum_state": None,
            "geometric_state": None
        }

        # Performance tracking
        self.performance_metrics = {
            "module_execution_times": {},
            "memory_usage": {},
            "computation_counts": {}
        }

        # Communication channels between modules
        self.message_channels = {}

        self.logger.info("CUEApplicationManager initialized")

    def initialize(self) -> None:
        """Initialize the application manager."""
        if self._is_initialized:
            return

        self.logger.info("Initializing CUE Application Manager...")

        # Initialize core system state
        self._initialize_system_state()

        # Initialize all registered modules if auto-initialization enabled
        if self.auto_initialize_modules:
            self.initialize_all_modules()

        self._is_initialized = True
        self.logger.info("CUE Application Manager initialization complete")

    def _initialize_system_state(self) -> None:
        """Initialize system-wide state variables."""
        device = self.device

        # Initialize global consciousness field
        self.system_state["consciousness_field"] = torch.randn(
            self.config.fiber_bundle_dim, device=device
        )

        # Initialize RG flow state
        self.system_state["rg_flow_state"] = {
            "kappa": torch.tensor(self.config.kappa, device=device),
            "beta_cog": torch.tensor(self.config.beta_cog, device=device), 
            "alpha_ent": torch.tensor(self.config.alpha_ent, device=device)
        }

        # Initialize quantum state
        self.system_state["quantum_state"] = torch.randn(
            256, device=device, dtype=torch.complex64
        )

        # Initialize geometric state (metric tensor)
        self.system_state["geometric_state"] = torch.eye(
            4, device=device
        )  # Minkowski metric as default

    def register_module(
        self,
        module: CUEBaseModule,
        category: str,
        dependencies: Optional[List[str]] = None,
        auto_initialize: bool = None
    ) -> None:
        """
        Register a module with the framework.

        Args:
            module: The module instance to register
            category: Module category (one of 14 categories)
            dependencies: List of module names this module depends on
            auto_initialize: Whether to initialize immediately
        """
        self.registry.register_module(module, category, dependencies)

        # Initialize if requested
        if auto_initialize or (auto_initialize is None and self.auto_initialize_modules):
            self._initialize_module_with_dependencies(module.name)

        self.logger.info(f"Registered module {module.name} in category {category}")

    def _initialize_module_with_dependencies(self, module_name: str) -> None:
        """Initialize module and its dependencies in correct order."""
        def init_recursive(name: str, visited: set):
            if name in visited:
                return
            visited.add(name)

            # Initialize dependencies first
            for dep_name in self.registry.dependencies.get(name, []):
                if dep_name in self.registry.modules:
                    init_recursive(dep_name, visited)

            # Initialize this module
            module = self.registry.get_module(name)
            if not module._is_initialized:
                module.initialize()
                self.logger.debug(f"Initialized module {name}")

        init_recursive(module_name, set())

    def initialize_all_modules(self) -> None:
        """Initialize all registered modules in dependency order."""
        self.logger.info("Initializing all modules...")

        for module_name in self.registry.initialization_order:
            module = self.registry.get_module(module_name)
            if not module._is_initialized:
                try:
                    module.initialize()
                    self.logger.debug(f"Initialized {module_name}")
                except Exception as e:
                    self.logger.error(f"Failed to initialize {module_name}: {e}")

        initialized_count = sum(
            1 for module in self.registry.modules.values()
            if module._is_initialized
        )

        self.logger.info(
            f"Initialized {initialized_count}/{len(self.registry.modules)} modules"
        )

    def get_module(self, name: str) -> CUEBaseModule:
        """Get module by name."""
        return self.registry.get_module(name)

    def get_modules_by_category(self, category: str) -> List[CUEBaseModule]:
        """Get all modules in a category."""
        return self.registry.get_modules_by_category(category)

    @contextmanager
    def experiment(self, name: str, description: str = "", config: Optional[Dict] = None):
        """Context manager for running experiments."""
        experiment_id = self.experiment_manager.create_experiment(name, description, config)
        self.experiment_manager.set_current_experiment(experiment_id)

        self.logger.info(f"Starting experiment: {name} (ID: {experiment_id[:8]})")

        try:
            yield experiment_id
        except Exception as e:
            self.logger.error(f"Experiment {name} failed: {e}")
            raise
        finally:
            self.logger.info(f"Experiment {name} completed")

    def run_consciousness_simulation(
        self,
        duration: int = 1000,
        consciousness_coupling: float = 0.1,
        save_results: bool = True
    ) -> Dict[str, Any]:
        """
        Run consciousness field simulation using available modules.

        Coordinates consciousness, quantum, and geometric modules
        for comprehensive consciousness-matter dynamics simulation.
        """
        if not self._is_initialized:
            self.initialize()

        self.logger.info(f"Running consciousness simulation for {duration} steps")

        # Get relevant modules
        consciousness_modules = self.get_modules_by_category("Cognitive_Dynamics")
        quantum_modules = self.get_modules_by_category("Quantum_Conscious_Interface")
        simulation_modules = self.get_modules_by_category("Simulation_Tools")

        results = {
            "duration": duration,
            "consciousness_coupling": consciousness_coupling,
            "consciousness_evolution": [],
            "quantum_states": [],
            "geometric_states": [],
            "timestamps": []
        }

        # Evolution loop
        for step in range(duration):
            timestamp = datetime.now()

            # Update consciousness field
            consciousness_state = self.system_state["consciousness_field"]

            # Apply consciousness dynamics
            for module in consciousness_modules:
                if hasattr(module, 'evolve_consciousness'):
                    consciousness_state = module.evolve_consciousness(
                        consciousness_state, dt=0.01
                    )

            # Update quantum state with consciousness coupling
            quantum_state = self.system_state["quantum_state"]
            for module in quantum_modules:
                if hasattr(module, 'apply_consciousness_coupling'):
                    quantum_state = module.apply_consciousness_coupling(
                        quantum_state, consciousness_state, consciousness_coupling
                    )

            # Update geometric state
            geometric_state = self.system_state["geometric_state"]

            # Store results
            if step % 10 == 0:  # Sample every 10 steps
                results["consciousness_evolution"].append(consciousness_state.clone().cpu())
                results["quantum_states"].append(quantum_state.clone().cpu())
                results["geometric_states"].append(geometric_state.clone().cpu())
                results["timestamps"].append(timestamp.isoformat())

            # Update system state
            self.system_state["consciousness_field"] = consciousness_state
            self.system_state["quantum_state"] = quantum_state
            self.system_state["geometric_state"] = geometric_state

            if step % 100 == 0:
                self.logger.debug(f"Simulation step {step}/{duration}")

        # Save results if requested
        if save_results and self.experiment_manager.current_experiment:
            self.experiment_manager.save_results({"consciousness_simulation": results})

        self.logger.info("Consciousness simulation completed")
        return results

    def compute(self, operation: str, **kwargs) -> Any:
        """
        Main computation method for coordinated module operations.

        Args:
            operation: Type of computation to perform
            **kwargs: Parameters for the operation
        """
        if not self._is_initialized:
            self.initialize()

        if operation == "consciousness_simulation":
            return self.run_consciousness_simulation(**kwargs)

        elif operation == "system_state":
            return self.get_system_state()

        elif operation == "module_status":
            return self.registry.get_status()

        else:
            raise ValueError(f"Unknown operation: {operation}")

    def get_system_state(self) -> Dict[str, Any]:
        """Get current system state."""
        return {
            "consciousness_field": self.system_state["consciousness_field"].cpu(),
            "rg_flow_state": {
                k: v.cpu() if torch.is_tensor(v) else v
                for k, v in self.system_state["rg_flow_state"].items()
            },
            "quantum_state": self.system_state["quantum_state"].cpu(),
            "geometric_state": self.system_state["geometric_state"].cpu(),
            "module_count": len(self.registry.modules),
            "initialized_modules": [
                name for name, module in self.registry.modules.items()
                if module._is_initialized
            ]
        }

    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance metrics summary."""
        return {
            "total_modules": len(self.registry.modules),
            "initialized_modules": len([
                m for m in self.registry.modules.values() if m._is_initialized
            ]),
            "execution_times": self.performance_metrics["module_execution_times"],
            "memory_usage": self.performance_metrics["memory_usage"],
            "computation_counts": self.performance_metrics["computation_counts"]
        }

    def save_configuration(self, filepath: str) -> None:
        """Save current configuration to file."""
        config_data = {
            "system_config": self.config.__dict__,
            "module_registry": self.registry.get_status(),
            "system_state_summary": {
                k: v.shape if torch.is_tensor(v) else str(type(v))
                for k, v in self.system_state.items()
            }
        }

        with open(filepath, "w") as f:
            json.dump(config_data, f, indent=2)

        self.logger.info(f"Configuration saved to {filepath}")

    def load_configuration(self, filepath: str) -> None:
        """Load configuration from file."""
        with open(filepath, "r") as f:
            config_data = json.load(f)

        # Update configuration
        for key, value in config_data["system_config"].items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)

        self.logger.info(f"Configuration loaded from {filepath}")
