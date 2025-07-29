"""
RG Flow Integrator Module

Implements renormalization group (RG) flow integration for the CUE Framework
coupling constants κ, β_cog, and α_ent. Provides analysis of fixed points,
flow trajectories, and critical behavior in the consciousness-matter system.

Based on CUE Framework RG flow equations (13-15).
"""

from typing import Dict, Any, Optional, List, Tuple, Callable
import torch
import numpy as np
from scipy.integrate import solve_ivp
from cueai_architect.base import CUEBaseModule, CUEConfiguration


class RGFlowIntegrator(CUEBaseModule):
    """
    Renormalization Group flow integrator for CUE Framework.
    
    Integrates the RG flow equations for coupling constants:
    - κ: Gravitational coupling
    - β_cog: Cognitive coupling strength  
    - α_ent: Entanglement parameter
    
    Provides fixed point analysis, flow trajectory computation,
    and critical behavior characterization.
    
    Attributes:
        flow_equations: RG flow equation system
        fixed_points: Detected fixed points
        flow_trajectories: Computed flow trajectories
        critical_exponents: Critical exponents at fixed points
    """
    
    def __init__(
        self,
        integration_method: str = "RK45",
        tolerance: float = 1e-8,
        max_flow_time: float = 100.0,
        config: Optional[CUEConfiguration] = None,
        **kwargs
    ):
        super().__init__(config=config, **kwargs)
        
        self.integration_method = integration_method
        self.tolerance = tolerance
        self.max_flow_time = max_flow_time
        
        # RG flow state
        self.current_couplings = None
        self.flow_trajectories = []
        self.fixed_points = []
        self.critical_exponents = {}
        
        # Flow equation parameters
        self.flow_parameters = {
            "lambda_gravity": 1.0,      # Gravitational flow parameter
            "lambda_consciousness": 0.5, # Consciousness flow parameter
            "lambda_entanglement": 0.3,  # Entanglement flow parameter
            "beta_0": 1.0,              # Leading beta function coefficient
            "gamma_anomalous": 0.1      # Anomalous dimension
        }
        
        self.logger.info(
            f"RGFlowIntegrator initialized: method={integration_method}, "
            f"tolerance={tolerance}"
        )
    
    def initialize(self) -> None:
        """Initialize RG flow integrator."""
        if self._is_initialized:
            return
        
        self.logger.info("Initializing RG flow integrator...")
        
        # Initialize coupling constants from configuration
        self.current_couplings = torch.tensor([
            self.config.kappa,      # κ
            self.config.beta_cog,   # β_cog
            self.config.alpha_ent   # α_ent
        ], device=self.device, dtype=torch.float64)
        
        # Clear previous results
        self.flow_trajectories.clear()
        self.fixed_points.clear()
        self.critical_exponents.clear()
        
        self._is_initialized = True
        self.logger.info("RG flow integrator initialization complete")
    
    def rg_flow_equations(self, t: float, couplings: np.ndarray) -> np.ndarray:
        """
        RG flow equations for CUE Framework coupling constants.
        
        Based on CUE equations (13-15):
        dκ/dt = β_κ(κ, β_cog, α_ent)
        dβ_cog/dt = β_β(κ, β_cog, α_ent)  
        dα_ent/dt = β_α(κ, β_cog, α_ent)
        
        Args:
            t: RG flow time (energy scale)
            couplings: [κ, β_cog, α_ent]
            
        Returns:
            Flow derivatives [dκ/dt, dβ_cog/dt, dα_ent/dt]
        """
        kappa, beta_cog, alpha_ent = couplings
        
        # β-function for gravitational coupling κ
        # β_κ = λ_g κ - a₁κ³ + a₂β_cog·α_ent
        beta_kappa = (
            self.flow_parameters["lambda_gravity"] * kappa
            - 0.1 * kappa**3
            + 0.05 * beta_cog * alpha_ent
        )
        
        # β-function for cognitive coupling β_cog
        # β_β = b₁β_cog² - b₂β_cog + b₃κ·α_ent
        beta_beta_cog = (
            0.1 * beta_cog**2
            - 0.05 * beta_cog
            + 0.02 * kappa * alpha_ent
        )
        
        # β-function for entanglement parameter α_ent
        # β_α = c₁α_ent - c₂α_ent² + c₃κ·β_cog
        beta_alpha_ent = (
            0.05 * alpha_ent
            - 0.1 * alpha_ent**2
            + 0.02 * kappa * beta_cog
        )
        
        return np.array([beta_kappa, beta_beta_cog, beta_alpha_ent])
    
    def integrate_flow(
        self,
        initial_couplings: Optional[torch.Tensor] = None,
        flow_time: Optional[float] = None,
        n_points: int = 1000
    ) -> Dict[str, Any]:
        """
        Integrate RG flow equations.
        
        Args:
            initial_couplings: Initial values [κ₀, β_cog₀, α_ent₀]
            flow_time: Maximum flow time
            n_points: Number of time points
            
        Returns:
            Dictionary with flow trajectory and analysis
        """
        if not self._is_initialized:
            self.initialize()
        
        if initial_couplings is None:
            initial_couplings = self.current_couplings
        
        if flow_time is None:
            flow_time = self.max_flow_time
        
        self.logger.info(f"Integrating RG flow for time {flow_time}")
        
        # Convert to numpy for scipy integration
        y0 = initial_couplings.cpu().numpy()
        t_span = (0, flow_time)
        t_eval = np.linspace(0, flow_time, n_points)
        
        # Integrate using scipy
        try:
            solution = solve_ivp(
                self.rg_flow_equations,
                t_span,
                y0,
                t_eval=t_eval,
                method=self.integration_method,
                rtol=self.tolerance,
                atol=self.tolerance
            )
            
            if not solution.success:
                self.logger.warning(f"RG flow integration failed: {solution.message}")
                return {"success": False, "message": solution.message}
            
        except Exception as e:
            self.logger.error(f"RG flow integration error: {e}")
            return {"success": False, "error": str(e)}
        
        # Convert back to torch tensors
        flow_trajectory = {
            "time": torch.tensor(solution.t, device=self.device),
            "kappa": torch.tensor(solution.y[0], device=self.device),
            "beta_cog": torch.tensor(solution.y[1], device=self.device),
            "alpha_ent": torch.tensor(solution.y[2], device=self.device)
        }
        
        # Store trajectory
        self.flow_trajectories.append(flow_trajectory)
        
        # Analyze flow
        analysis = self._analyze_flow_trajectory(flow_trajectory)
        
        results = {
            "success": True,
            "trajectory": flow_trajectory,
            "analysis": analysis,
            "final_couplings": torch.tensor(solution.y[:, -1], device=self.device)
        }
        
        self.log_computation("rg_flow_integration", results)
        return results
    
    def find_critical_points(
        self,
        search_bounds: Optional[List[Tuple[float, float]]] = None,
        n_search_points: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Find fixed points (critical points) of the RG flow.
        
        Fixed points satisfy: β_κ = β_β = β_α = 0
        
        Args:
            search_bounds: Search bounds [(κ_min, κ_max), (β_min, β_max), (α_min, α_max)]
            n_search_points: Number of search points per dimension
            
        Returns:
            List of fixed points with stability analysis
        """
        if not self._is_initialized:
            self.initialize()
        
        if search_bounds is None:
            search_bounds = [(-2.0, 2.0), (-2.0, 2.0), (-2.0, 2.0)]
        
        self.logger.info("Searching for RG flow fixed points...")
        
        fixed_points = []
        
        # Grid search for fixed points
        kappa_range = np.linspace(*search_bounds[0], n_search_points)
        beta_range = np.linspace(*search_bounds[1], n_search_points)
        alpha_range = np.linspace(*search_bounds[2], n_search_points)
        
        for kappa in kappa_range[::5]:  # Coarse grid first
            for beta_cog in beta_range[::5]:
                for alpha_ent in alpha_range[::5]:
                    
                    # Check if close to fixed point
                    couplings = np.array([kappa, beta_cog, alpha_ent])
                    flow_derivatives = self.rg_flow_equations(0, couplings)
                    
                    if np.linalg.norm(flow_derivatives) < 0.1:  # Coarse threshold
                        # Refine using root finding
                        try:
                            from scipy.optimize import fsolve
                            
                            refined_point = fsolve(
                                lambda x: self.rg_flow_equations(0, x),
                                couplings,
                                xtol=self.tolerance
                            )
                            
                            # Verify it's actually a fixed point
                            residual = self.rg_flow_equations(0, refined_point)
                            if np.linalg.norm(residual) < self.tolerance:
                                
                                # Check if already found
                                is_new = True
                                for existing_fp in fixed_points:
                                    if np.linalg.norm(existing_fp["couplings"] - refined_point) < 0.01:
                                        is_new = False
                                        break
                                
                                if is_new:
                                    # Analyze stability
                                    stability = self._analyze_fixed_point_stability(refined_point)
                                    
                                    fixed_point = {
                                        "couplings": refined_point,
                                        "kappa": refined_point[0],
                                        "beta_cog": refined_point[1], 
                                        "alpha_ent": refined_point[2],
                                        "stability": stability,
                                        "residual_norm": np.linalg.norm(residual)
                                    }
                                    
                                    fixed_points.append(fixed_point)
                                    
                        except Exception as e:
                            self.logger.debug(f"Fixed point refinement failed: {e}")
                            continue
        
        self.fixed_points = fixed_points
        self.logger.info(f"Found {len(fixed_points)} fixed points")
        
        return fixed_points
    
    def _analyze_fixed_point_stability(self, fixed_point: np.ndarray) -> Dict[str, Any]:
        """
        Analyze stability of fixed point using linearization.
        
        Computes Jacobian matrix and eigenvalues to determine stability.
        """
        # Compute Jacobian matrix numerically
        epsilon = 1e-6
        jacobian = np.zeros((3, 3))
        
        for i in range(3):
            # Forward difference
            point_plus = fixed_point.copy()
            point_plus[i] += epsilon
            flow_plus = self.rg_flow_equations(0, point_plus)
            
            point_minus = fixed_point.copy()
            point_minus[i] -= epsilon
            flow_minus = self.rg_flow_equations(0, point_minus)
            
            jacobian[:, i] = (flow_plus - flow_minus) / (2 * epsilon)
        
        # Compute eigenvalues
        eigenvalues = np.linalg.eigvals(jacobian)
        
        # Classify stability
        real_parts = np.real(eigenvalues)
        
        if np.all(real_parts < 0):
            stability_type = "stable"
        elif np.all(real_parts > 0):
            stability_type = "unstable"
        else:
            stability_type = "saddle"
        
        return {
            "type": stability_type,
            "eigenvalues": eigenvalues,
            "jacobian": jacobian,
            "critical_exponents": -real_parts  # Critical exponents
        }
    
    def _analyze_flow_trajectory(self, trajectory: Dict[str, torch.Tensor]) -> Dict[str, Any]:
        """Analyze flow trajectory for interesting features."""
        
        # Compute flow speed
        dt = trajectory["time"][1] - trajectory["time"][0]
        
        kappa_flow = torch.diff(trajectory["kappa"]) / dt
        beta_flow = torch.diff(trajectory["beta_cog"]) / dt
        alpha_flow = torch.diff(trajectory["alpha_ent"]) / dt
        
        flow_speed = torch.sqrt(kappa_flow**2 + beta_flow**2 + alpha_flow**2)
        
        # Find slow flow regions (near fixed points)
        slow_flow_threshold = 0.01
        slow_regions = flow_speed < slow_flow_threshold
        
        # Compute invariant quantities (if any)
        # Example: κ² + β_cog² + α_ent² (not necessarily conserved)
        invariant = (
            trajectory["kappa"]**2 + 
            trajectory["beta_cog"]**2 + 
            trajectory["alpha_ent"]**2
        )
        
        analysis = {
            "flow_speed": flow_speed,
            "max_flow_speed": torch.max(flow_speed).item(),
            "min_flow_speed": torch.min(flow_speed).item(),
            "slow_flow_regions": slow_regions,
            "invariant_quantity": invariant,
            "invariant_variation": torch.std(invariant).item(),
            "final_couplings": {
                "kappa": trajectory["kappa"][-1].item(),
                "beta_cog": trajectory["beta_cog"][-1].item(),
                "alpha_ent": trajectory["alpha_ent"][-1].item()
            }
        }
        
        return analysis
    
    def compute_beta_functions(self, couplings: torch.Tensor) -> torch.Tensor:
        """
        Compute β-functions at given coupling values.
        
        Args:
            couplings: Tensor of shape (..., 3) with [κ, β_cog, α_ent]
            
        Returns:
            β-function values of same shape
        """
        if not self._is_initialized:
            self.initialize()
        
        # Convert to numpy for computation
        couplings_np = couplings.cpu().numpy()
        original_shape = couplings_np.shape
        
        # Flatten for vectorized computation
        if couplings_np.ndim > 1:
            couplings_flat = couplings_np.reshape(-1, 3)
            beta_functions = np.array([
                self.rg_flow_equations(0, coupling)
                for coupling in couplings_flat
            ])
            beta_functions = beta_functions.reshape(original_shape)
        else:
            beta_functions = self.rg_flow_equations(0, couplings_np)
        
        return torch.tensor(beta_functions, device=self.device)
    
    def compute(self, operation: str = "integrate_flow", **kwargs) -> Any:
        """Main computation method."""
        if operation == "integrate_flow":
            return self.integrate_flow(**kwargs)
        elif operation == "find_fixed_points":
            return self.find_critical_points(**kwargs)
        elif operation == "beta_functions":
            return self.compute_beta_functions(**kwargs)
        else:
            raise ValueError(f"Unknown operation: {operation}")
    
    def get_flow_summary(self) -> Dict[str, Any]:
        """Get comprehensive summary of RG flow analysis."""
        return {
            "current_couplings": self.current_couplings.cpu().numpy() if self.current_couplings is not None else None,
            "n_trajectories": len(self.flow_trajectories),
            "n_fixed_points": len(self.fixed_points),
            "fixed_points": [
                {
                    "couplings": fp["couplings"].tolist(),
                    "stability": fp["stability"]["type"]
                }
                for fp in self.fixed_points
            ],
            "flow_parameters": self.flow_parameters
        }
    
    def visualize_flow(self, projection: str = "2d"):
        """Create visualization of RG flow."""
        if not self.flow_trajectories:
            self.logger.warning("No flow trajectories to visualize")
            return None
        
        try:
            import matplotlib.pyplot as plt
            from mpl_toolkits.mplot3d import Axes3D
            
            if projection == "3d":
                fig = plt.figure(figsize=(12, 9))
                ax = fig.add_subplot(111, projection='3d')
                
                # Plot trajectories
                for i, traj in enumerate(self.flow_trajectories):
                    ax.plot(
                        traj["kappa"].cpu().numpy(),
                        traj["beta_cog"].cpu().numpy(),
                        traj["alpha_ent"].cpu().numpy(),
                        label=f"Trajectory {i+1}",
                        alpha=0.7
                    )
                
                # Plot fixed points
                for fp in self.fixed_points:
                    color = 'red' if fp["stability"]["type"] == "stable" else 'blue'
                    ax.scatter(
                        fp["kappa"], fp["beta_cog"], fp["alpha_ent"],
                        color=color, s=100, marker='*'
                    )
                
                ax.set_xlabel('κ (Gravitational)')
                ax.set_ylabel('β_cog (Cognitive)')
                ax.set_zlabel('α_ent (Entanglement)')
                ax.set_title('RG Flow in Coupling Space')
                ax.legend()
                
            else:  # 2D projections
                fig, axes = plt.subplots(1, 3, figsize=(18, 6))
                
                projections = [
                    ("kappa", "beta_cog", "κ", "β_cog"),
                    ("kappa", "alpha_ent", "κ", "α_ent"),
                    ("beta_cog", "alpha_ent", "β_cog", "α_ent")
                ]
                
                for ax, (x_key, y_key, x_label, y_label) in zip(axes, projections):
                    # Plot trajectories
                    for i, traj in enumerate(self.flow_trajectories):
                        ax.plot(
                            traj[x_key].cpu().numpy(),
                            traj[y_key].cpu().numpy(),
                            label=f"Trajectory {i+1}",
                            alpha=0.7
                        )
                    
                    # Plot fixed points
                    for fp in self.fixed_points:
                        color = 'red' if fp["stability"]["type"] == "stable" else 'blue'
                        ax.scatter(
                            fp[x_key.replace("_", "")], fp[y_key.replace("_", "")],
                            color=color, s=100, marker='*'
                        )
                    
                    ax.set_xlabel(x_label)
                    ax.set_ylabel(y_label)
                    ax.set_title(f'RG Flow: {x_label} vs {y_label}')
                    ax.grid(True, alpha=0.3)
                
                axes[0].legend()
            
            plt.tight_layout()
            return fig
            
        except ImportError:
            self.logger.warning("matplotlib not available for visualization")
            return None
