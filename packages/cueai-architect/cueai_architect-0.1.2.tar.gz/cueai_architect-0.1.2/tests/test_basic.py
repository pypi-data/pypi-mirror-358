"""
Basic test for CUE-AI Architect functionality
"""

import pytest
import torch
import numpy as np
from cueai_architect.base import CUEConfiguration, CUEBaseModule


class TestCUEConfiguration:
    """Test CUE configuration dataclass."""

    def test_default_configuration(self):
        """Test default configuration values."""
        config = CUEConfiguration()

        assert config.kappa == 1.0
        assert config.beta_cog == 0.5
        assert config.alpha_ent == 0.3
        assert config.consciousness_coupling == 0.1
        assert config.fiber_bundle_dim == 64
        assert config.coherence_threshold == 0.7
        assert config.tolerance == 1e-8
        assert config.max_iterations == 1000
        assert config.device == "cpu"
        assert config.log_level == "INFO"

    def test_custom_configuration(self):
        """Test custom configuration values."""
        config = CUEConfiguration(
            kappa=2.0,
            consciousness_coupling=0.2,
            fiber_bundle_dim=128,
            device="cuda" if torch.cuda.is_available() else "cpu"
        )

        assert config.kappa == 2.0
        assert config.consciousness_coupling == 0.2
        assert config.fiber_bundle_dim == 128


class MockCUEModule(CUEBaseModule):
    """Mock module for testing base functionality."""

    def initialize(self):
        self._is_initialized = True
        self._state["test_value"] = 42

    def compute(self, x):
        return x * 2


class TestCUEBaseModule:
    """Test base module functionality."""

    def test_module_creation(self):
        """Test module creation and initialization."""
        config = CUEConfiguration()
        module = MockCUEModule(config=config, name="TestModule")

        assert module.name == "TestModule"
        assert module.config == config
        assert not module._is_initialized
        assert isinstance(module.id, str)
        assert len(module.id) == 36  # UUID length

    def test_module_initialization(self):
        """Test module initialization."""
        module = MockCUEModule()

        assert not module._is_initialized
        module.initialize()
        assert module._is_initialized
        assert module._state["test_value"] == 42

    def test_module_computation(self):
        """Test module computation."""
        module = MockCUEModule()
        result = module.compute(5)
        assert result == 10

    def test_module_state_management(self):
        """Test module state get/set."""
        module = MockCUEModule()
        module.initialize()

        state = module.get_state()
        assert state["name"] == "MockCUEModule"
        assert state["is_initialized"] is True
        assert state["state"]["test_value"] == 42

        new_state = {"state": {"test_value": 100, "new_key": "test"}}
        module.set_state(new_state)

        updated_state = module.get_state()
        assert updated_state["state"]["test_value"] == 100
        assert updated_state["state"]["new_key"] == "test"

    def test_tensor_device_handling(self):
        """Test tensor device handling."""
        config = CUEConfiguration(device="cpu")
        module = MockCUEModule(config=config)

        tensor = torch.randn(3, 4)
        device_tensor = module.to_device(tensor)

        assert device_tensor.device.type == "cpu"


if __name__ == "__main__":
    # Run basic tests
    print("🧪 Running basic CUE-AI Architect tests...")

    # Test configuration
    config_test = TestCUEConfiguration()
    config_test.test_default_configuration()
    config_test.test_custom_configuration()
    print("✅ Configuration tests passed")

    # Test base module
    module_test = TestCUEBaseModule()
    module_test.test_module_creation()
    module_test.test_module_initialization()
    module_test.test_module_computation()
    module_test.test_module_state_management()
    module_test.test_tensor_device_handling()
    print("✅ Base module tests passed")

    print("🎉 All basic tests completed successfully!")
