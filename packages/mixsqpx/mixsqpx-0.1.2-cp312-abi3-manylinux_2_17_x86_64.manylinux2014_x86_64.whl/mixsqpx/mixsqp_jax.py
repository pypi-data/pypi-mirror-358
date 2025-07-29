# Copyright (c) 2025 Jackson Bunting, Paul Diegert, and Arnaud Maurel
# License: MIT

"""
mixsqp_jax.py

JAX interface for the mixSQP algorithm.

This module provides a JAX-compatible wrapper for the mixSQP solver, which 
is an algorithm for maximum likelihood estimation of finite mixtures with 
known component densities. The main entry point is the `mixsolve` 
function, which is JIT-compilable and exposes all tuning parameters 
for advanced users.

References
----------
- R mixSQP package: https://github.com/stephenslab/mixSQP
- Kim, Y., Carbonetto, P., Stephens, M., & Anitescu, M. (2020). 
  A Fast Algorithm for Maximum Likelihood Estimation of Mixture Proportions Using Sequential Quadratic Programming.
  Journal of Computational and Graphical Statistics, 29(2), 261–273.

Typical usage example:

    import jax.numpy as jnp
    from mixsqpx.mixsqp_jax import mixsolve

    lclk = jnp.array(...)  # log-likelihood matrix, shape (n, k)
    weights, jacobian, hessian = mixsolve(lclk)

"""

import jax
import numpy as np

from . import cpu_ops

jax.ffi.register_ffi_target("mixsqp", cpu_ops.cpu_mixsqp_ffi(), platform="cpu")

def mixsolve(
    lclk: jax.numpy.ndarray, 
    verbose: bool = False,
    num_iter_em: int = 10,
    zero_threshold_solution: float = 1e-8,
    tol_svd: float = 1e-6,
    control_sqp: float = 1e-8,
    convtol_active_set: float = 1e-10,
    zero_threshold_searchdir: float = 1e-14,
    suffdecr_linesearch: float = 1e-2,
    stepsizereduce: float = 0.75,
    minstepsize: float = 1e-8,
    identity_contrib_increase: float = 10.0,
    maxiter_sqp: int = 1000,
    maxiter_activeset: int = 20
):
    """
    Solve the mixture weights in MLE estimation problem for a finite mixture with 
    known component densities using the mixSQP algorithm.

    This function estimates the mixture proportions that maximize the likelihood
    given a matrix of log-likelihoods for each observation and mixture component.
    It is JIT-compilable and suitable for use in JAX pipelines.

    Parameters
    ----------
    lclk : jax.numpy.ndarray
        Log-likelihood matrix of shape (n_samples, n_components).
        Each entry lclk[i, j] is the log-likelihood of sample i under component j.
    verbose : bool, optional
        If True, print progress and diagnostic information (default: False).
    num_iter_em : int, optional
        Number of EM iterations to perform before switching to SQP (default: 10).
    zero_threshold_solution : float, optional
        Threshold below which solution entries are set to zero (default: 1e-8).
    tol_svd : float, optional
        Tolerance for singular value decomposition in the SQP step (default: 1e-6).
    control_sqp : float, optional
        Convergence tolerance for the SQP algorithm (default: 1e-8).
    convtol_active_set : float, optional
        Convergence tolerance for the active set method (default: 1e-10).
    zero_threshold_searchdir : float, optional
        Threshold for zeroing small entries in the search direction (default: 1e-14).
    suffdecr_linesearch : float, optional
        Sufficient decrease parameter for line search (default: 1e-2).
    stepsizereduce : float, optional
        Factor to reduce step size during line search (default: 0.75).
    minstepsize : float, optional
        Minimum step size allowed in line search (default: 1e-8).
    identity_contrib_increase : float, optional
        Amount to increase diagonal of Hessian for numerical stability (default: 10.0).
    maxiter_sqp : int, optional
        Maximum number of SQP iterations (default: 1000).
    maxiter_activeset : int, optional
        Maximum number of active set iterations (default: 20).

    Returns
    -------
    solution : jax.numpy.ndarray
        Estimated mixture proportions (length n_components).
    status : jax.numpy.ndarray
        Status information (length n_components).
    hessian : jax.numpy.ndarray
        Hessian matrix at the solution (shape n_components x n_components).

    Notes
    -----
    This function is JIT-compiled with static arguments for all solver parameters
    except the log-likelihood matrix.

    If the input log-likelihood matrix contains NaNs, the outputs will also be all-NaN.
    This "propagation" of NaNs is intended to signal error conditions to the caller.
    """
    _, nsupp = lclk.shape

    call = jax.ffi.ffi_call(
        "mixsqp",
        [
            jax.ShapeDtypeStruct((nsupp,), jax.numpy.float64),
            jax.ShapeDtypeStruct((nsupp,), jax.numpy.float64),
            jax.ShapeDtypeStruct((nsupp, nsupp), jax.numpy.float64)
        ]
    )

    return call(
        lclk.T, 
        verbose=np.int8(verbose),
        num_iter_em=np.int32(num_iter_em),
        zero_threshold_solution=zero_threshold_solution,
        tol_svd=tol_svd,
        control_sqp=control_sqp,
        convtol_active_set=convtol_active_set,
        zero_threshold_searchdir=zero_threshold_searchdir,
        suffdecr_linesearch=suffdecr_linesearch,
        stepsizereduce=stepsizereduce,
        minstepsize=minstepsize,
        identity_contrib_increase=identity_contrib_increase,
        maxiter_sqp=np.int32(maxiter_sqp),
        maxiter_activeset=np.int32(maxiter_activeset)
    )

mixsolve = jax.jit(mixsolve, static_argnums = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13))