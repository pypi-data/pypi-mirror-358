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

import jax
from jax import numpy as jnp

from ..recurrent import recurrent


def lightning_attn(
    q: jax.Array,
    k: jax.Array,
    v: jax.Array,
    layer_idx: int,
    num_layers: int,
    scale: float | None = None,
    initial_state: jax.Array | None = None,
    reverse: bool = False,
    cu_seqlens: jax.Array | None = None,
) -> tuple[jax.Array, jax.Array]:
    """
    Computes Lightning Attention using a recurrent, linear-time mechanism.

    This function implements the Lightning Attention mechanism, a form of linear
    attention where the decay rate (`g_gamma`) is dynamically determined by the
    layer's depth within the model. This allows for different temporal receptive
    fields across layers.

    The computation is performed efficiently using a recurrent formulation,
    making it suitable for long sequences. It serves as a specialized wrapper
    around the generic `recurrent` function and supports both standard batch
    processing and packed variable-length inputs via `cu_seqlens`.

    Args:
        q: The query tensor. Expected shape is `(batch, seq_len, num_heads, head_dim)`
            or `(1, total_tokens, num_heads, head_dim)` if `cu_seqlens` is used.
        k: The key tensor. Must have the same shape as `q`.
        v: The value tensor. Must have the same shape as `q`.
        layer_idx: The 0-indexed index of the current layer, used to compute
            the layer-specific decay factor.
        num_layers: The total number of layers in the model.
        scale: A scaling factor applied to the query. If `None`, it defaults
            to `1 / sqrt(head_dim)`.
        initial_state: The initial hidden state for the recurrence. Useful for
            chunked processing of long sequences.
        reverse: If `True`, the sequence is processed in reverse order.
        cu_seqlens: Cumulative sequence lengths for variable-length inputs.
            This is a 1D tensor like `[0, len_seq1, len_seq1+len_seq2, ...]`.
            If provided, the input tensors are expected to be "packed" with a
            batch size of 1.

    Returns:
        A tuple containing:
            - o (jax.Array): The output tensor, with the same shape as `q`.
            - final_state (jax.Array): The final hidden state of the recurrence.

    Raises:
        ValueError: If `cu_seqlens` is provided and the batch size of `q` is
            not 1.
        ValueError: If `cu_seqlens` is provided and the number of initial states
            does not match the number of sequences.
    """
    if cu_seqlens is not None:
        if q.shape[0] != 1:
            raise ValueError(
                f"The batch size is expected to be 1 rather than {q.shape[0]} when using `cu_seqlens`."
                f"Please flatten variable-length inputs before processing."
            )
        if initial_state is not None and initial_state.shape[0] != len(cu_seqlens) - 1:
            raise ValueError(
                f"The number of initial states is expected to be equal to the number of input sequences, "
                f"i.e., {len(cu_seqlens) - 1} rather than {initial_state.shape[0]}."
            )
    if scale is None:
        scale = k.shape[-1] ** -0.5
    qheads = q.shape[2]
    g_gamma = -(8 / qheads * (1 - layer_idx / num_layers)) * jnp.arange(qheads, dtype="f4")
    return recurrent(
        q=q,
        k=k,
        v=v,
        g_gamma=g_gamma,
        scale=scale,
        initial_state=initial_state,
        reverse=reverse,
        cu_seqlens=cu_seqlens,
    )
