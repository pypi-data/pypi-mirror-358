# Copyright 2021 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Modifications copyright (C) 2024 S.Cao
# ported Google's Jax-CFD functional template to PyTorch's tensor ops

from typing import Callable, Dict, Optional, Tuple, Union

import torch
import torch.fft as fft
import torch.nn as nn
from einops import repeat
import torch_cfd.grids as grids

Grid = grids.Grid
Params = Union[nn.ParameterDict, Dict]

def fft_mesh_2d(n, diam, device=None):
    kx, ky = [fft.fftfreq(n, d=diam / n) for _ in range(2)]
    kx, ky = torch.meshgrid([kx, ky], indexing="ij")
    return kx.to(device), ky.to(device)


def fft_expand_dims(fft_mesh, batch_size):
    kx, ky = fft_mesh
    kx, ky = [repeat(z, "x y -> b x y 1", b=batch_size) for z in [kx, ky]]
    return kx, ky


def spectral_laplacian_2d(fft_mesh, device=None):
    kx, ky = fft_mesh
    lap = -4 * (torch.pi**2) * (abs(kx) ** 2 + abs(ky) ** 2)
    lap[..., 0, 0] = 1
    return lap.to(device)


def spectral_curl_2d(vhat, rfft_mesh):
    r"""
    Computes the 2D curl in the Fourier basis.
    det [d_x d_y \\ u v]
    """
    uhat, vhat = vhat
    kx, ky = rfft_mesh
    return 2j * torch.pi * (vhat * kx - uhat * ky)


def spectral_div_2d(vhat, rfft_mesh):
    r"""
    Computes the 2D divergence in the Fourier basis.
    """
    uhat, vhat = vhat
    kx, ky = rfft_mesh
    return 2j * torch.pi * (uhat * kx + vhat * ky)


def spectral_grad_2d(vhat, rfft_mesh):
    kx, ky = rfft_mesh
    return 2j * torch.pi * kx * vhat, 2j * torch.pi * ky * vhat


def spectral_rot_2d(vhat, rfft_mesh):
    vgradx, vgrady = spectral_grad_2d(vhat, rfft_mesh)
    return vgrady, -vgradx


def brick_wall_filter_2d(grid: Grid):
    """Implements the 2/3 rule.
    Modification to the original Jax-CFD code
    according to https://github.com/google/jax-cfd/pull/245
    """
    n, m = grid.shape
    filter_ = torch.zeros((n, m // 2 + 1))
    filter_[:(int(2 / 3 * n) // 2 + 1), :int(2 / 3 * (m // 2 + 1))] = 1
    filter_[-int(2 / 3 * n) // 2 :, : int(2 / 3 * (m // 2 + 1))] = 1
    return filter_


def vorticity_to_velocity(
    grid: Grid, w_hat: torch.Tensor, rfft_mesh: Optional[Tuple[torch.Tensor, ...]] = None
):
    """Constructs a function for converting vorticity to velocity, both in Fourier domain.

    Solves for the stream function and then uses the stream function to compute
    the velocity. This is the standard approach. A quick sketch can be found in
    [1].

    Args:
        grid: the grid underlying the vorticity field.

    Returns:
        A function that takes a vorticity (rfftn) and returns a velocity vector
        field.

    Reference:
        [1] Z. Yin, H.J.H. Clercx, D.C. Montgomery, An easily implemented task-based
        parallel scheme for the Fourier pseudospectral solver applied to 2D
        Navier-Stokes turbulence, Computers & Fluids, Volume 33, Issue 4, 2004,
        Pages 509-520, ISSN 0045-7930,
        https://doi.org/10.1016/j.compfluid.2003.06.003.
    """
    kx, ky = rfft_mesh if rfft_mesh is not None else grid.rfft_mesh()
    assert kx.shape[-2:] == w_hat.shape[-2:]
    laplace = spectral_laplacian_2d((kx, ky))
    psi_hat = -1 / laplace * w_hat
    u_hat, v_hat = spectral_rot_2d(psi_hat, (kx, ky))
    return (u_hat, v_hat), psi_hat


def stable_time_step(
    dx: float = 1,
    dt: float = 1,
    max_velocity: float = 1.0,
    max_courant_number: float = 0.5,
    viscosity: float = 1e-3,
    implicit_diffusion: bool = True,
    ndim: int = 2,
) -> float:
    """
    Calculate a stable time step satisfying the CFL condition
    for the explicit advection term
    if the diffusion is explicit, the time step is the smaller
    of the advection and diffusion time steps.

    Args:
    max_velocity: maximum velocity.
    max_courant_number: the Courant number used to choose the time step. Smaller
      numbers will lead to more stable simulations. Typically this should be in
      the range [0.5, 1).
    dx: spatial mesh size, can be min(grid.step).
    dt: time step.
    """
    dt_diffusion = dx

    if not implicit_diffusion:
        dt_diffusion = dx**2 / (viscosity * 2 ** (ndim))
    dt_advection = max_courant_number * dx / max_velocity
    dt = dt_advection if dt is None else dt
    return min(dt_diffusion, dt_advection, dt)


class ImplicitExplicitODE(nn.Module):
    r"""Describes a set of ODEs with implicit & explicit terms.

    The equation is given by:
      $\partial u/ \partial t = N(u) + Lu$
      where L is linear, N(\cdot) is nonlinear.

    Then, the IMEX scheme in general is
      $\partial u/ \partial t = explicit_terms(u) + implicit_terms(u)$

    `explicit_terms(u)` is for N(u) that should use explicit time-stepping
    `implicit_terms(u)` is for Lu that uses an implicit solver.

    Typically the explicit terms are non-linear and the implicit terms are linear.
    This simplifies solves but isn't strictly necessary.
    """

    def explicit_terms(self, u, t: Optional[float] = 0.0):
        """Evaluates explicit terms in the ODE."""
        raise NotImplementedError

    def implicit_terms(self, u):
        """Evaluates implicit terms in the ODE."""
        raise NotImplementedError

    def implicit_solve(
        self,
        u: torch.Tensor,
        step_size: float,
    ):
        """Solves `u - step_size * implicit_terms(u) = f` for u."""
        raise NotImplementedError

    def residual(
        self,
        u: torch.Tensor,
        u_t: torch.Tensor,
        t: Optional[float] = 0.0,
    ):
        """Computes the residual of the PDE."""
        raise NotImplementedError



class IMEXStepper(nn.Module):
    """
    Implicit-Explicit (IMEX) time stepping with configurable order.

    Supports:
    - order=1: Forward-Backward Euler, implicit for the diffusion (first-order accuracy)
    - order=1.5: Standard IMEX Crank-Nicolson, CR for the diffusion.
    - order=2: RK2 Crank-Nicolson (second-order accuracy)
        - With alpha=0.5: Heun's method (midpoint rule)
        - With alpha=2/3: Ralston's method (minimizes truncation error)

    Args:
      order: Order of accuracy (1, 1.5, or 2)
      alpha: RK weight parameter (default: 0.5 for Heun's method)
      beta: Weight for implicit step (default: 0.5 for standard CN, 1.0 for order=1)
      requires_grad: Whether parameters should be trainable

    References:
      - (RK) Chandler, G. J. & Kerswell, R. R. Invariant recurrent solutions embedded in
      a turbulent two-dimensional Kolmogorov flow. J. Fluid Mech. 722, 554-595
      (2013). https://doi.org/10.1017/jfm.2013.122 (Section 3)
      - https://en.wikipedia.org/wiki/List_of_Runge%E2%80%93Kutta_methods
    """

    def __init__(
        self,
        order: float = 2,
        alpha: float = 0.5,
        beta: Optional[float] = 0.5,
        requires_grad: bool = False,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.order = order

        # Set default beta based on order
        params = {
            "alpha": torch.tensor(alpha),
            "beta": torch.tensor(beta),
        }
        if order == 1 or order == 1.5:
            # Order 1: Forward-Backward Euler (no parameters needed)
            # alpha = 1.0
            # Order 1.5: Standard IMEX Crank-Nicolson
            # alpha = 0.5
            self.stepper = self._imex
        elif order == 2:
            # Order 2: RK2 Crank-Nicolson
            self.stepper = self._rk2_crank_nicolson

        self._set_params(params, requires_grad=requires_grad)

    @property
    def order(self):
        return self._order

    @order.setter
    def order(self, value):
        self._order = value


    def _set_params(self, params: Params, requires_grad: bool = False):
        """Set the RK coefficients."""
        for k, v in params.items():
            if not isinstance(v, nn.Parameter):
                v = nn.Parameter(v)
        self.params = nn.ParameterDict(params)
        if not requires_grad:
            for k, v in self.params.items():
                v.requires_grad = False
        self.requires_grad = requires_grad

    def _imex(
        self,
        u: torch.Tensor,
        dt: float,
        equation: ImplicitExplicitODE,
        t: Optional[float] = 0.0,
        params: Optional[Params] = None,
    ) -> torch.Tensor:
        """Standard IMEX with Crank-Nicolson or Forward-Backward Euler."""
        params = self.params if params is None else params
        alpha = params["alpha"]

        F = equation.explicit_terms
        G = equation.implicit_terms
        G_inv = equation.implicit_solve

        g = u + dt * F(u, t) + (1 - alpha) * dt * G(u)
        u = G_inv(g, alpha * dt)
        return u
    
    def _backward_forward_euler(
        self,
        u: torch.Tensor,
        dt: float,
        equation: ImplicitExplicitODE,
        t: Optional[float] = 0.0,
        params: Optional[Params] = None
    ) -> torch.Tensor:
        """Forward-Backward Euler implementation (order 1)."""
        F = equation.explicit_terms
        G_inv = equation.implicit_solve

        g = u + dt * F(u, t)
        u = G_inv(g, dt)
        return u

    def _rk2_crank_nicolson(
        self,
        u: torch.Tensor,
        dt: float,
        equation: ImplicitExplicitODE,
        t: Optional[float] = 0.0,
        params: Optional[Params] = None,
    ) -> torch.Tensor:
        """RK2 Crank-Nicolson implementation (order 2)."""
        params = self.params if params is None else params
        alpha = params["alpha"]
        beta = params["beta"]

        F = equation.explicit_terms
        G = equation.implicit_terms
        G_inv = equation.implicit_solve

        g = u + beta * dt * G(u)
        h = F(u, t)
        u = G_inv(g + dt * h, beta * dt)

        h = alpha * F(u, t) + (1 - alpha) * h
        u = G_inv(g + dt * h, beta * dt)
        return u

    def forward(
        self,
        u: torch.Tensor,
        dt: float,
        equation: ImplicitExplicitODE,
        t: Optional[float] = 0.0,
        params: Optional[Params] = None,
    ) -> torch.Tensor:
        """
        Perform a time step using the configured IMEX scheme.

        Input:
            u^{t_i}: (B, *, n, n)

        Returns:
            u^{t_{i+1}} (B, *, n, n)
        """
        return self.stepper(u, dt, equation, t, params)


class RK4CrankNicolsonStepper(IMEXStepper):
    """
    RK4CrankNicholsonStepper is ported from jax functional programming to follow
    the standard tensor2tensor format of nn.Module
    Time stepping via
    - either "low-storage" Runge-Kutta and Crank-Nicolson steps.
    https://github.com/google/jax-cfd/blob/main/jax_cfd/spectral/time_stepping.py#L117
    - or standard RK4 coefficients (classic 4-stage RK4)

    These scheme are second order accurate for the implicit terms, but potentially
    higher order accurate for the explicit terms. This seems to be a favorable
    tradeoff when the explicit terms dominate, e.g., for modeling turbulent
    fluids.

    Per Canuto: "[these methods] have been widely used for the time-discretization
    in applications of spectral methods."

    Args:
      alphas: alpha coefficients.
      betas: beta coefficients.
      gammas: gamma coefficients.
      equation.F: explicit terms (convection, rhs, drag).
      equation.G: implicit terms (diffusion).
      equation.implicit_solve: implicit solver, when evaluates at an input (B, n, n), outputs (B, n, n).
      dt: time step.

    Reference:
      Canuto, C., Yousuff Hussaini, M., Quarteroni, A. & Zang, T. A.
      Spectral Methods: Evolution to Complex Geometries and Applications to
      Fluid Dynamics. (Springer Berlin Heidelberg, 2007).
      https://doi.org/10.1007/978-3-540-30728-0 (Appendix D.3)
    """

    def __init__(
        self,
        order: float = 4,
        requires_grad: bool = False,
        weights: Optional[Params] = None,
        low_storage: bool = True,
        *args,
        **kwargs,
    ):
        super().__init__(order, *args, **kwargs)
        if low_storage:
            # Carpenter-Kennedy coefficients
            weights = {
                "alphas": [
                    0,
                    0.1496590219993,
                    0.3704009573644,
                    0.6222557631345,
                    0.9582821306748,
                    1,
                ],
                "betas": [
                    0,
                    -0.4178904745,
                    -1.192151694643,
                    -1.697784692471,
                    -1.514183444257,
                ],
                "gammas": [
                    0.1496590219993,
                    0.3792103129999,
                    0.8229550293869,
                    0.6994504559488,
                    0.1530572479681,
                ],
            }
        else:
            # Standard RK4 coefficients (classic 4-stage RK4)
            weights = {
                "alphas": [0, 0.5, 0.5, 1.0, 1.0],
                "betas": [0, 0, 0, 0],
                "gammas": [1 / 6, 1 / 3, 1 / 3, 1 / 6],
            }
        params = {k: torch.tensor(v) for k, v in weights.items()}
        self._set_params(params, requires_grad=requires_grad)

    def forward(
        self,
        u: torch.Tensor,
        dt: float,
        equation: ImplicitExplicitODE,
        t: Optional[float] = 0.0,
        params: Optional[Params] = None,
    ) -> torch.Tensor:
        """
        Input:
            - w^{t_i} (B, n, n)
            - dt: time step
            - params: RK coefficients optional to override
        Returns: w^{t_{i+1}} (B, n, n)
        """
        params = self.params if params is None else params
        alphas = params["alphas"]
        betas = params["betas"]
        gammas = params["gammas"]
        F = equation.explicit_terms
        G = equation.implicit_terms
        G_inv = equation.implicit_solve

        if len(alphas) - 1 != len(betas) != len(gammas):
            raise ValueError("number of RK coefficients does not match")

        h = 0
        for k in range(len(betas)):
            h = F(u, t) + betas[k] * h
            mu = 0.5 * dt * (alphas[k + 1] - alphas[k])
            u = G_inv(u + gammas[k] * dt * h + mu * G(u), mu)
        return u


class NavierStokes2DSpectral(ImplicitExplicitODE):
    """Breaks the Navier-Stokes equation into implicit and explicit parts.

    Implicit parts are the linear terms and explicit parts are the non-linear
    terms.

    Attributes:
      viscosity: strength of the diffusion term
      grid: underlying grid of the process
      smooth: smooth the advection term using the 2/3-rule.
      forcing_fn: forcing function, if None then no forcing is used.
      drag: strength of the drag. Set to zero for no drag.
    """

    def __init__(
        self,
        viscosity: float,
        grid: Grid,
        drag: float = 0.0,
        smooth: bool = True,
        forcing_fn: Optional[Callable] = None,
        step_fn: IMEXStepper = IMEXStepper(),
    ):
        super().__init__()
        self.viscosity = viscosity
        self.grid = grid
        self.drag = drag
        self.smooth = smooth
        self.forcing_fn = forcing_fn
        self.step_fn = step_fn
        self._initialize()

    def _initialize(self):
        kx, ky = self.grid.rfft_mesh()
        self.register_buffer("kx", kx)
        self.register_buffer("ky", ky)
        laplace = -4 * (torch.pi) ** 2 * (abs(kx) ** 2 + abs(ky) ** 2)
        self.register_buffer("laplace", laplace)
        filter_ = brick_wall_filter_2d(self.grid)
        linear_term = self.viscosity * laplace - self.drag
        self.register_buffer("linear_term", linear_term)
        self.register_buffer("filter", filter_)

    def residual(
        self,
        vhat: torch.Tensor,
        vt_hat: torch.Tensor,
        t: Optional[float] = 0.0,
    ):
        residual = vt_hat - self.explicit_terms(vhat, t) - self.implicit_terms(vhat)
        return residual

    def _explicit_terms(self, vort_hat: torch.Tensor, t: Optional[float] = 0.0):
        kx, ky = torch.as_tensor(self.kx), torch.as_tensor(self.ky)
        vhat, _ = vorticity_to_velocity(self.grid, vort_hat, (kx, ky))
        vx, vy = fft.irfft2(vhat[0]), fft.irfft2(vhat[1])

        grad_x_hat = 2j * torch.pi * kx * vort_hat
        grad_y_hat = 2j * torch.pi * ky * vort_hat
        grad_x, grad_y = fft.irfft2(grad_x_hat), fft.irfft2(grad_y_hat)

        advection = -(grad_x * vx + grad_y * vy)
        advection_hat = fft.rfft2(advection)

        if self.smooth:
            advection_hat *= self.filter

        terms = advection_hat

        if self.forcing_fn is not None:
            if not self.forcing_fn.vorticity:
                fx, fy = self.forcing_fn(self.grid, (vx, vy), t)
                fx_hat, fy_hat = fft.rfft2(fx.data), fft.rfft2(fy.data)
                terms += spectral_curl_2d((fx_hat, fy_hat), (kx, ky))
            else:
                f = self.forcing_fn(self.grid, vort_hat, t)
                f_hat = fft.rfft2(f.data)
                terms += f_hat.expand_as(vort_hat)
        return terms

    def explicit_terms(self, vort_hat, t: Optional[float] = 0.0):
        return self._explicit_terms(vort_hat, t)

    def implicit_terms(self, vort_hat):
        return self.linear_term * vort_hat

    def implicit_solve(self, vort_hat, dt):
        return 1 / (1 - dt * self.linear_term) * vort_hat

    def step(self, *args, **kwargs):
        return self.forward(*args, **kwargs)

    def forward(
        self,
        vort_hat: torch.Tensor,
        dt: float,
        steps: int = 1,
        t: Optional[float] = 0.0,
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Args:
            vort_hat: (B, kx, ky) or (n_t, kx, ky) or (kx, ky)
            - if rfft2 is used then the shape is (*, nx, ny//2+1)
            - if (n_t, kx, ky), then the time step marches in the time
            dimension in parallel.
            dt: time step.
            steps: number of steps to take, default is 1.
            t: time, used for forcing function.
        Returns:
            vort_hat: (B, kx, ky) or (n_t, kx, ky) or (kx, ky)
            dvortdt_hat: (B, kx, ky) or (n_t, kx, ky) or (kx, ky).
        """
        vort_old = vort_hat
        for _ in range(steps):
            vort_hat = self.step_fn(vort_hat, dt, self, t)
        dvortdt_hat = 1 / (steps * dt) * (vort_hat - vort_old)
        return vort_hat, dvortdt_hat
