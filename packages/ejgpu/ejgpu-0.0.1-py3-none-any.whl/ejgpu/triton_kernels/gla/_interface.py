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

from ..recurrent import recurrent


def recurrent_gla(
    q: jax.Array,
    k: jax.Array,
    v: jax.Array,
    g: jax.Array = None,
    g_gamma: jax.Array = None,
    scale: float | None = None,
    initial_state: jax.Array | None = None,
    reverse: bool = False,
    cu_seqlens: jax.Array | None = None,
) -> tuple[jax.Array, jax.Array]:
    """
    Computes Gated Linear Attention (GLA) in a recurrent, linear-time manner.

    This function provides a convenient wrapper around the core `recurrent`
    implementation, tailored for GLA. It processes sequences step-by-step,
    making it highly efficient for very long sequences and suitable for
    autoregressive decoding.

    It supports both standard batch processing and variable-length sequence
    processing using cumulative sequence lengths (`cu_seqlens`).

    Args:
        q: The query tensor. Expected shape is `(batch, seq_len, num_heads, head_dim)`
            or `(total_tokens, num_heads, head_dim)` if `cu_seqlens` is used.
        k: The key tensor. Must have the same shape as `q`.
        v: The value tensor. Must have the same shape as `q`.
        g: The gate tensor, specific to Gated Linear Attention. If provided, it
            should have the same shape as `q`.
        g_gamma: The gate decay factor.
        scale: A scaling factor applied to the query before the recurrent
            computation. If `None`, it defaults to `1 / sqrt(head_dim)`.
        initial_state: The initial hidden state for the recurrence. Useful for
            chunked processing of long sequences.
        reverse: If `True`, the sequence is processed in reverse order.
        cu_seqlens: Cumulative sequence lengths for variable-length inputs.
            This is a 1D tensor like `[0, len_seq1, len_seq1+len_seq2, ...]`.
            If provided, the input tensors `q, k, v, g` are expected to be
            "packed" with a shape of `(total_tokens, ...)`.

    Returns:
        A tuple containing:
            - o (jax.Array): The output tensor, with the same shape as `q`.
            - final_state (jax.Array): The final hidden state of the recurrence,
              which can be used as `initial_state` for a subsequent segment.

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
    o, final_state = recurrent(
        q=q,
        k=k,
        v=v,
        g=g,
        g_gamma=g_gamma,
        scale=scale,
        initial_state=initial_state,
        reverse=reverse,
        cu_seqlens=cu_seqlens,
    )
    return o, final_state
