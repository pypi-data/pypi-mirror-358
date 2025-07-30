"""
mixsqpx: A Jax-compatible interface to the mixSQP algorithm.

MIT License

Copyright (c) 2025 Jackson Bunting, Paul Diegert, Arnaud Maurel

This project contains code adapted from mixSQP,
Copyright (c) 2017-2020, Youngseok Kim, Peter Carbonetto, Matthew Stephens and Mihai Anitescu,
also available under the MIT License.
"""

__all__ = ["mixsolve"]

import jax
from mixsqpx.mixsqp_jax import mixsolve

# Enable 64 bit floating point precision
jax.config.update("jax_enable_x64", True)

# We use the CPU instead of GPU und mute all warnings if no GPU/TPU is found.
jax.config.update('jax_platform_name', 'cpu')
