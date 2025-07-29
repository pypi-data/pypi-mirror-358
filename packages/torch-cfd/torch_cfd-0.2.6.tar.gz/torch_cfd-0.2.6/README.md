# Neural Operator-Assisted Computational Fluid Dynamics in PyTorch
[![Python 3.10](https://img.shields.io/badge/python-3.10-blue.svg)](https://www.python.org/downloads/release/python-3100) ![CFD tests](https://github.com/scaomath/torch-cfd/actions/workflows/pytest.yml/badge.svg)

![A decaying turbulence (McWilliams 1984)](examples/McWilliams2d.svg)

## A native PyTorch port of [Google's Computational Fluid Dynamics package in Jax](https://github.com/google/jax-cfd)
This port is a good pedagogical tool to learn how to implement traditional numerical solvers using modern deep learning software interfaces. The main changes are documented in the [`torch_cfd` directory](./torch_cfd/). The most significant changes in all routines include:
  - (**enhanced**) Nonhomogenous/immersed boundary conditions support: the user can provide array-valued or function-valued boundary conditions, and can add a no-slip mask when there are obstacles. Many routines in Jax-CFD only work with only periodic or constant boundary.
  - (**changed**) Routines that rely on the functional programming of Jax have been rewritten to be the PyTorch's tensor-in-tensor-out style, which is arguably more user-friendly to debugging as one can view intermediate values in tensors in VS Code debugger, opposed to Jax's `JaxprTrace`.
  - (**enhanced**) Batch-dimension: all operations take into consideration the batch dimension of tensors `(b, *, n, m)` regardless of `*` dimension, for example, `(b, T, C, n, m)`, which is similar to PyTorch behavior. In the original Jax-CFD package, only a single trajectory is implemented. The stencil operators are changed to generally operate from the last dimension using negative indexing, following `torch.nn.functional.pad`'s behavior.
  - (**changed**) Neural Network interface: functions and operators are in general implemented as `nn.Module` like a factory template.
  - (**enhanced**) Jax-CFD's `funcutils.trajectory` function supports tracking only one field variable (vorticity or velocity). In Torch-CFD, extra fields computation and tracking are more accessible and easier for user to add, such as time derivatives $\partial_t\mathbf{u}_h$ and PDE residual $R(\mathbf{u}_h):=\mathbf{f}-\partial_t \mathbf{u}_h-(\mathbf{u}_h\cdot\nabla)\mathbf{u}_h + \nu \Delta \mathbf{u}_h$.


## Neural Operator-Assisted Navier-Stokes Equations simulator.
  - The **Spatiotemporal Fourier Neural Operator** (SFNO) is a spacetime tensor-to-tensor learner (or trajectory-to-trajectory), available in the [`fno` directory](./fno). Different components of FNO have been re-implemented keeping the conciseness of the original implementation while allowing modern expansions. We draw inspiration from the [3D FNO in Nvidia's Neural Operator repo](https://github.com/neuraloperator/neuraloperator), [Transformers-based neural operators](https://github.com/thuml/Neural-Solver-Library), as well as Temam's book on functional analysis for the NSE. 
  - Major architectural changes: learnable spatiotemporal positional encodings, layernorm to replace a hard-coded global Gaussian normalizer, and many others. For more details please see [the documentation of the `SFNO` class](./fno/sfno.py#L485). 
  - Data generations:
    - Isotropic turbulence in McWilliams, J. C. (1984). The emergence of isolated coherent vortices in turbulent flow. *Journal of Fluid Mechanics*, 146, 21-43. After the warmup phase, the energy spectra match the direct cascade in a periodic box.
    - Forced turbulence example: Kolmogorov flow with inverse cascades.
  - Pipelines for the *a posteriori* error estimation to fine-tune the SFNO to reach the scientific computing level of accuracy ($\le 10^{-6}$) in Bochner norm using FLOPs on par with a single evaluation, and only a fraction of FLOPs of a single `.backward()`.
  - [Examples](#examples) can be found below.


## Examples
- Demos of different simulation setups:
  - [von Kármán vortex street](./examples/von_Karman_vortex_rk4_fvm.ipynb)
  - [2D Lid-driven cavity with a random field perturbation using finite volume](./examples/Lid-driven_cavity_rk4_fvm.ipynb)
  - [2D decaying isotropic turbulence using the pseudo-spectral method](./examples/Kolmogrov2d_rk4_spectral_forced_turbulence.ipynb)
  - [2D Kolmogorov flow using finite volume method](./examples/Kolmogrov2d_rk4_fvm_forced_turbulence.ipynb)
- Demos of Spatiotemporal FNO's training and evaluation using the neural operator-assisted fluid simulation pipelines
  - [Training of SFNO for only 15 epochs for the isotropic turbulence example](./examples/ex2_SFNO_train.ipynb)
  - [Training of SFNO for only ***10*** epochs with 1k samples and reach `1e-2` level of relative error](./examples/ex2_SFNO_train_fnodata.ipynb) using the data in the FNO paper, which to our best knowledge no operator learner can do this in <100 epochs in the small data regime.
  - [Fine-tuning of SFNO on a `256x256` grid for only 50 ADAM iterations to reach `1e-6` residual in the functional norm using FNO data](./examples/ex2_SFNO_finetune_fnodata.ipynb)
  - [Fine-tuning of SFNO on the `256x256` grid for the McWilliams 2d isotropic turbulence](./examples/ex2_SFNO_finetune_McWilliams2d.ipynb)
  - [Training of SFNO for only 5 epoch to match the inverse cascade of Kolmogorov flow](./examples/ex2_SFNO_5ep_spectra.ipynb)
  - [Baseline of FNO3d for fixed step size that requires preloading a normalizer](./examples/ex2_FNO3d_train_normalized.ipynb)

## Installation
To install `torch-cfd`'s current release, simply do:
```bash
pip install torch-cfd
```

If one wants to play with the neural operator part, it is recommended to clone this repo and play it locally by creating a venv using [`requirements.txt`](./requirements.txt). Note: even you do not want to install dependencies, using PyTorch version >=2.0.0 is recommended for the broadcasting semantics.
```bash
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Data
The data are available at [https://huggingface.co/datasets/scaomath/navier-stokes-dataset](https://huggingface.co/datasets/scaomath/navier-stokes-dataset).
Data generation instructions are available in the [SFNO folder](./fno).

## Licenses
The Apache 2.0 License in the root folder applies to the `torch-cfd` folder of the repo that is inherited from Google's original license file for `Jax-cfd`. The `fno` folder has the MIT license inherited from [NVIDIA's Neural Operator repo](https://github.com/neuraloperator/neuraloperator). Note: the license(s) in the subfolder takes precedence.

## Contributions
PR welcome for enhancing [essential functionalities with TODO tags](./torch_cfd/README.md). Currently, the port of `torch-cfd` currently includes:
- The pseudospectral method for vorticity uses anti-aliasing filtering techniques for nonlinear terms to maintain stability.
- The finite volume method using MAC grids for velocity, together with a simple pressure projection scheme to impose the divergence free condition.
- Temporal discretization: Currently it has only single-step RK4-family schemes uses explicit time-stepping for advection, either implicit or explicit time-stepping for diffusion.
- Boundary conditions: 
  - velocity: periodic, Dirichlet (function-valued or array-valued), Dirichlet-Neumann (Neumann has to be 0-valued).
  - pressure: periodic, Neumann, Neumann-Dirichlet mixed. 
- Solvers: 
  - Pseudo-inverse (either FFT-based or SVD based)
  - Jacobi-, Gauss-Seidel-, or Multigrid V-cycle-preconditioned Conjugate gradient.

## Reference

If you like to use `torch-cfd` please use the following [paper](https://arxiv.org/abs/2405.17211) as citation. 

```bibtex
@inproceedings{2025SpectralRefiner,
  title     = {Spectral-Refiner: Accurate Fine-Tuning of Spatiotemporal Fourier Neural Operator for Turbulent Flows},
  author    = {Shuhao Cao and Francesco Brarda and Ruipeng Li and Yuanzhe Xi},
  booktitle = {The Thirteenth International Conference on Learning Representations},
  year      = {2025},
  url       = {https://openreview.net/forum?id=MKP1g8wU0P},
  eprint    = {arXiv:2405.17211},
}
```

## Acknowledgments
I am grateful for the support from [Long Chen (UC Irvine)](https://github.com/lyc102/ifem) and 
[Ludmil Zikatanov (Penn State)](https://github.com/HAZmathTeam/hazmath) over the years, and their efforts in open-sourcing scientific computing codes. I also appreciate the support from the National Science Foundation (NSF) to junior researchers. I want to thank the free A6000 credits at the SSE ML cluster from the University of Missouri. 

(Added after `0.2.0`) I also want to acknowledge that University of Missouri's OpenAI Enterprise API key. After version `0.1.0`, I began prompt in VSCode Copilot with existing codes (using the OpenAI Enterprise API), which arguably significantly improve the efficiency on "porting->debugging->refactoring" cycle, e.g., Copilot helps design unittests and `.vscode/launch.json` for debugging. For details of how Copilot's suggestions on code refactoring, please see [README.md](./torch_cfd/README.md) in `torch_cfd` folder.

For individual paper's acknowledgment please see [here](./fno/README.md).
