"""
Tests for PreMetricSubstrate module
"""

import pytest
import torch
import numpy as np
from cueai_architect.base import CUEConfiguration
from cueai_architect.core.foundations.pre_metric_substrate import PreMetricSubstrate


class TestPreMetricSubstrate:
    """Test PreMetricSubstrate functionality."""

    def test_initialization(self):
        """Test substrate initialization."""
        config = CUEConfiguration(manifold_resolution=32)
        substrate = PreMetricSubstrate(
            manifold_resolution=32,
            proto_coherence_lambda=1.5,
            config=config
        )
        
        assert substrate.manifold_resolution == 32
        assert substrate.proto_coherence_lambda == 1.5
        assert not substrate._is_initialized
        
        # Initialize
        substrate.initialize()
        assert substrate._is_initialized
        
        # Check fields are created
        assert substrate.psi_protocoherence is not None
        assert substrate.phi_dark_precursor is not None
        assert substrate.xi_vector_field is not None
        assert substrate.zeta_vector_field is not None
        assert substrate.topological_tension is not None
        assert substrate.relational_oscillator is not None

    def test_proto_action_computation(self):
        """Test proto-action computation."""
        substrate = PreMetricSubstrate(manifold_resolution=16)
        substrate.initialize()
        
        proto_action = substrate.compute_proto_action()
        
        assert isinstance(proto_action, torch.Tensor)
        assert proto_action.dim() == 0  # Scalar
        assert torch.isfinite(proto_action)
        
        # Check components
        components = substrate.proto_action_components
        assert "oscillator_term" in components
        assert "derivative_term" in components
        assert "tension_term" in components
        assert "total_action" in components

    def test_geometric_instabilities(self):
        """Test geometric instability detection."""
        substrate = PreMetricSubstrate(manifold_resolution=16)
        substrate.initialize()
        
        instabilities = substrate.detect_geometric_instabilities()
        
        assert isinstance(instabilities, torch.Tensor)
        assert instabilities.dtype == torch.bool
        assert instabilities.shape == (16, 16, 16, 16)  # 4D manifold

    def test_compute_method(self):
        """Test main compute method."""
        substrate = PreMetricSubstrate(manifold_resolution=16)
        
        results = substrate.compute()
        
        assert isinstance(results, dict)
        assert "proto_action" in results
        assert "psi_field" in results
        assert "phi_field" in results
        assert "topological_tension" in results
        assert "action_components" in results

    def test_field_gradients(self):
        """Test field gradient computation."""
        substrate = PreMetricSubstrate(manifold_resolution=8)
        substrate.initialize()
        
        # Test gradient computation
        psi_grad = substrate._compute_field_gradient(substrate.psi_protocoherence)
        phi_grad = substrate._compute_field_gradient(substrate.phi_dark_precursor)
        
        assert psi_grad.shape[-1] == 4  # 4D manifold
        assert phi_grad.shape[-1] == 4
        assert torch.isfinite(psi_grad).all()
        assert torch.isfinite(phi_grad).all()

    def test_visualization(self):
        """Test visualization method."""
        substrate = PreMetricSubstrate(manifold_resolution=8)
        substrate.initialize()
        
        # Test without matplotlib (should return None)
        fig = substrate.visualize_substrate()
        # Will return None if matplotlib not available, or figure if available
        assert fig is None or hasattr(fig, 'savefig')


if __name__ == "__main__":
    # Run tests
    print("🧪 Running PreMetricSubstrate tests...")
    
    test_suite = TestPreMetricSubstrate()
    test_suite.test_initialization()
    print("✅ Initialization test passed")
    
    test_suite.test_proto_action_computation()
    print("✅ Proto-action computation test passed")
    
    test_suite.test_geometric_instabilities()
    print("✅ Geometric instabilities test passed")
    
    test_suite.test_compute_method()
    print("✅ Compute method test passed")
    
    test_suite.test_field_gradients()
    print("✅ Field gradients test passed")
    
    test_suite.test_visualization()
    print("✅ Visualization test passed")
    
    print("🎉 All PreMetricSubstrate tests completed successfully!")
