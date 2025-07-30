# Copyright 2023 The EASYDEL/EJGPU(EasyDeLJaxGPUUtilities) Author @erfanzar (Erfan Zare Chavoshi).
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from functools import partial

import jax

from ._triton_impl_bwd import bwd_triton_impl
from ._triton_impl_fwd import fwd_triton_impl


def _fwd_call(x: jax.Array, chunk_size: int, cu_seqlens: jax.Array | None = None):
    """
    Forward pass for mean pooling with custom VJP.

    Args:
        x: The input tensor.
        chunk_size: The chunk size for processing.
        cu_seqlens: Optional cumulative sequence lengths for variable-length sequences.

    Returns:
        A tuple containing the output of the forward pass and the residuals
        needed for the backward pass.
    """
    o = fwd_triton_impl(x=x, chunk_size=chunk_size, cu_seqlens=cu_seqlens)
    residual = x.shape[0], x.shape[1], cu_seqlens
    return o, residual


def _bwd_call(chunk_size, residual: tuple[jax.Array], do: jax.Array):
    """
    Backward pass for mean pooling with custom VJP.

    Args:
        chunk_size: The chunk size used in the forward pass.
        residual: Residuals saved from the forward pass.
        do: The gradient of the output tensor.

    Returns:
        The gradient with respect to the input tensor `x`.
    """
    A, B, cu_seqlens = residual
    dEo = bwd_triton_impl(do=do, batch_size=A, seq_len=B, chunk_size=chunk_size, cu_seqlens=cu_seqlens)
    return dEo


@partial(jax.custom_vjp, nondiff_argnums=(1,))
@partial(jax.jit, static_argnums=(1,))
def _mean_pooling(x: jax.Array, chunk_size: int, cu_seqlens: jax.Array | None = None) -> jax.Array:
    """
    Core JIT-compiled mean pooling function with a custom VJP.

    This is an internal function that directly calls the Triton implementation
    for the forward pass and is registered with JAX's custom differentiation
    system.

    Args:
        x: The input tensor.
        chunk_size: The chunk size for processing, a static argument for JIT.
        cu_seqlens: Optional cumulative sequence lengths for variable-length sequences.

    Returns:
        The mean-pooled output tensor.
    """
    return fwd_triton_impl(x=x, chunk_size=chunk_size, cu_seqlens=cu_seqlens)


_mean_pooling.defvjp(_fwd_call, _bwd_call)


def mean_pooling(x: jax.Array, chunk_size: int, cu_seqlens: jax.Array | None = None) -> jax.Array:
    """
    Performs mean pooling over the sequence dimension using a Triton kernel.

    This function calculates the mean of token embeddings for each sequence in a
    batch. It is optimized for GPUs using a custom Triton kernel and supports
    both standard (padded) and variable-length sequences.

    Args:
        x: The input tensor of shape `(batch_size, sequence_length, hidden_dim)`.
            If `cu_seqlens` is provided for variable-length inputs, the shape
            should be `(total_tokens, hidden_dim)`.
        chunk_size: A performance-tuning parameter for the Triton kernel that
            determines how the input is chunked for processing.
        cu_seqlens: An optional 1D tensor of cumulative sequence lengths for
            handling variable-length sequences in a packed format.
            Example: `[0, len_seq1, len_seq1+len_seq2, ...]`. If provided, the
            function will compute the mean pooling for each of the packed
            sequences.

    Returns:
        A tensor of shape `(batch_size, hidden_dim)` containing the mean-pooled
        embeddings for each sequence. If `cu_seqlens` is used, the batch size in
        the output shape will correspond to the number of sequences defined by
        `cu_seqlens` (i.e., `len(cu_seqlens) - 1`).
    """
    return _mean_pooling(x=x, chunk_size=chunk_size, cu_seqlens=cu_seqlens)
