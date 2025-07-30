"""
*Experimental* implementation of FlashAttention in Triton.
Tested with triton==2.0.0.dev20221202.
Triton 2.0 has a new backend (MLIR) but seems like it doesn't yet work for head dimensions
other than 64:
https://github.com/openai/triton/blob/d376020f90002757eea3ea9475d4f7cfc2ec5ead/python/triton/ops/flash_attention.py#L207
We'll update this implementation with the new Triton backend once this is fixed.

We use the FlashAttention implementation from Phil Tillet a starting point.
https://github.com/openai/triton/blob/master/python/tutorials/06-fused-attention.py

Changes:
- Implement both causal and non-causal attention.
- Implement both self-attention and cross-attention.
- Support arbitrary seqlens (not just multiples of 128), for both forward and backward.
- Support all head dimensions up to 128 (not just 16, 32, 64, 128), for both forward and backward.
- Support attention bias.
- Speed up the forward pass a bit, and only store the LSE instead of m and l.
- Make the backward for d=128 much faster by reducing register spilling.
- Optionally parallelize the backward pass across seqlen_k, to deal with the case of
small batch size * nheads.

Caution:
- This is an *experimental* implementation. The forward pass should be quite robust but
I'm not 100% sure that the backward pass doesn't have race conditions (due to the Triton compiler).
- This implementation has only been tested on A100.
- If you plan to use headdim other than 64 and 128, you should test for race conditions
(due to the Triton compiler), as done in tests/test_flash_attn.py
"test_flash_attn_triton_race_condition". I've tested and fixed many race conditions
for different head dimensions (40, 48, 64, 128, 80, 88, 96), but I'm still not 100% confident
that there are none left for other head dimensions.

Differences between this Triton version and the CUDA version:
- Triton version doesn't support dropout.
- Triton forward is generally faster than CUDA forward, while Triton backward is
generally slower than CUDA backward. Overall Triton forward + backward is slightly slower
than CUDA forward + backward.
- Triton version doesn't support different sequence lengths in a batch (i.e., RaggedTensor/NestedTensor).
- Triton version supports attention bias, while CUDA version doesn't.
"""

import math

import torch
import triton
import triton.language as tl


# Disabling autotune for now, set num_warps=4 if headdim=64 and num_warps=8 if headdim=128
# @triton.autotune(
#     configs=[
#         triton.Config({"BLOCK_M": 128, "BLOCK_N": 128}, num_warps=4, num_stages=1),
#         # This config has a race condition when EVEN_M == False, disabling it for now.
#         # triton.Config({"BLOCK_M": 64, "BLOCK_N": 64}, num_warps=4, num_stages=1),
#     ],
#     key=['CACHE_KEY_SEQLEN_Q', 'CACHE_KEY_SEQLEN_K', 'BIAS_TYPE', 'IS_CAUSAL', 'BLOCK_HEADDIM']
# )
@triton.heuristics(
    {
        "EVEN_M": lambda args: args["seqlen_q"] % args["BLOCK_M"] == 0,
        "EVEN_N": lambda args: args["seqlen_k"] % args["BLOCK_N"] == 0,
        "EVEN_HEADDIM": lambda args: args["headdim"] == args["BLOCK_HEADDIM"],
    }
)
@triton.jit
def _fwd_kernel(
    Q,
    K,
    V,
    Bias,
    Out,
    Lse,
    TMP,  # NOTE: TMP is a scratchpad buffer to workaround a compiler bug
    softmax_scale,
    stride_qb,
    stride_qh,
    stride_qm,
    stride_kb,
    stride_kh,
    stride_kn,
    stride_vb,
    stride_vh,
    stride_vn,
    stride_bb,
    stride_bh,
    stride_bm,
    stride_ob,
    stride_oh,
    stride_om,
    nheads,
    seqlen_q,
    seqlen_k,
    seqlen_q_rounded,
    headdim,
    CACHE_KEY_SEQLEN_Q,
    CACHE_KEY_SEQLEN_K,
    BIAS_TYPE: tl.constexpr,
    IS_CAUSAL: tl.constexpr,
    BLOCK_HEADDIM: tl.constexpr,
    EVEN_M: tl.constexpr,
    EVEN_N: tl.constexpr,
    EVEN_HEADDIM: tl.constexpr,
    BLOCK_M: tl.constexpr,
    BLOCK_N: tl.constexpr,
):
    """
    _fwd_kernel is a Triton implementation of the forward pass of FlashAttention.

    Args:
        Q (torch.Tensor): Query tensor of shape (batch_size, sequence_length, num_heads, head_dim)
        K (torch.Tensor): Key tensor of shape (batch_size, sequence_length, num_heads, head_dim)
        V (torch.Tensor): Value tensor of shape (batch_size, sequence_length, num_heads, head_dim)
        Bias (torch.Tensor): Bias tensor for the attention scores. Can be of shape (batch_size, num_heads, 1, sequence_length) or (batch_size, num_heads, sequence_length, sequence_length)
        Out (torch.Tensor): Output tensor where the results are to be stored
        Lse (torch.Tensor): Tensor to store log-sum-exp of the attention scores
        TMP (torch.Tensor): Temporary scratchpad tensor to workaround a compiler bug
        stride_qb (int): Stride for the batch dimension in the query tensor
        stride_qh (int): Stride for the head dimension in the query tensor
        stride_qm (int): Stride for the sequence dimension in the query tensor
        stride_kb (int): Stride for the batch dimension in the key tensor
        stride_kh (int): Stride for the head dimension in the key tensor
        stride_kn (int): Stride for the sequence dimension in the key tensor
        stride_vb (int): Stride for the batch dimension in the value tensor
        stride_vh (int): Stride for the head dimension in the value tensor
        stride_vn (int): Stride for the sequence dimension in the value tensor
        stride_bb (int): Stride for the batch dimension in the bias tensor
        stride_bh (int): Stride for the head dimension in the bias tensor
        stride_bm (int): Stride for the sequence dimension in the bias tensor
        stride_ob (int): Stride for the batch dimension in the output tensor
        stride_oh (int): Stride for the head dimension in the output tensor
        stride_om (int): Stride for the sequence dimension in the output tensor
        nheads (int): Number of attention heads
        seqlen_q (int): Sequence length for the query tensor
        seqlen_k (int): Sequence length for the key tensor
        seqlen_q_rounded (int): Rounded up sequence length for the query tensor
        headdim (int): Dimension of each attention head
        CACHE_KEY_SEQLEN_Q (int): Cached sequence length for the query tensor
        CACHE_KEY_SEQLEN_K (int): Cached sequence length for the key tensor
        BIAS_TYPE (tl.constexpr): Type of bias used. Can be 'none', 'vector', or 'matrix'
        IS_CAUSAL (tl.constexpr): Whether the attention is causal or not
        BLOCK_HEADDIM (tl.constexpr): Block size for the head dimension
        EVEN_M (tl.constexpr): Whether the sequence length for the query tensor is divisible by the block size
        EVEN_N (tl.constexpr): Whether the sequence length for the key tensor is divisible by the block size
        EVEN_HEADDIM (tl.constexpr): Whether the head dimension is divisible by the block size
        BLOCK_M (tl.constexpr): Block size for the sequence dimension in the query tensor
        BLOCK_N (tl.constexpr): Block size for the sequence dimension in the key tensor
    """
    start_m = tl.program_id(0)
    off_hb = tl.program_id(1)
    off_b = off_hb // nheads
    off_h = off_hb % nheads
    # off_b = tl.program_id(1)
    # off_h = tl.program_id(2)
    # off_hb = off_b * nheads + off_h
    # initialize offsets
    offs_m = start_m * BLOCK_M + tl.arange(0, BLOCK_M)
    offs_n = tl.arange(0, BLOCK_N)
    offs_d = tl.arange(0, BLOCK_HEADDIM)
    # Initialize pointers to Q, K, V
    # Adding parenthesis around indexing might use int32 math instead of int64 math?
    # https://github.com/openai/triton/issues/741
    # I'm seeing a tiny bit of difference (5-7us)
    q_ptrs = (
        Q
        + off_b * stride_qb
        + off_h * stride_qh
        + (offs_m[:, None] * stride_qm + offs_d[None, :])
    )
    k_ptrs = (
        K
        + off_b * stride_kb
        + off_h * stride_kh
        + (offs_n[:, None] * stride_kn + offs_d[None, :])
    )
    v_ptrs = (
        V
        + off_b * stride_vb
        + off_h * stride_vh
        + (offs_n[:, None] * stride_vn + offs_d[None, :])
    )
    if BIAS_TYPE == "vector":
        b_ptrs = Bias + off_b * stride_bb + off_h * stride_bh + offs_n
    elif BIAS_TYPE == "matrix":
        b_ptrs = (
            Bias
            + off_b * stride_bb
            + off_h * stride_bh
            + (offs_m[:, None] * stride_bm + offs_n[None, :])
        )
    # initialize pointer to m and l
    t_ptrs = TMP + off_hb * seqlen_q_rounded + offs_m
    # For softpick:
    # max_i stores the running maximum of scores.
    # sum_abs_val_i stores the running sum of absolute differences for normalization.
    max_i = tl.zeros([BLOCK_M], dtype=tl.float32) - float("inf")
    sum_abs_val_i = tl.zeros([BLOCK_M], dtype=tl.float32)
    acc_o = tl.zeros([BLOCK_M, BLOCK_HEADDIM], dtype=tl.float32)

    # load q: it will stay in SRAM throughout
    if EVEN_M & EVEN_N:  # Bug fix for Triton compiler as in original
        if EVEN_HEADDIM:
            q = tl.load(q_ptrs)
        else:
            q = tl.load(q_ptrs, mask=offs_d[None, :] < headdim, other=0.0)
    else:
        if EVEN_HEADDIM:
            q = tl.load(q_ptrs, mask=offs_m[:, None] < seqlen_q, other=0.0)
        else:
            q = tl.load(
                q_ptrs,
                mask=(offs_m[:, None] < seqlen_q) & (offs_d[None, :] < headdim),
                other=0.0,
            )

    # loop over k, v and update accumulator
    end_n = seqlen_k if not IS_CAUSAL else tl.minimum((start_m + 1) * BLOCK_M, seqlen_k)
    for start_n in range(0, end_n, BLOCK_N):
        start_n = tl.multiple_of(start_n, BLOCK_N)
        # -- load k, v --
        if EVEN_N & EVEN_M:
            if EVEN_HEADDIM:
                k = tl.load(k_ptrs + start_n * stride_kn)
            else:
                k = tl.load(
                    k_ptrs + start_n * stride_kn,
                    mask=offs_d[None, :] < headdim,
                    other=0.0,
                )
        else:
            if EVEN_HEADDIM:
                k = tl.load(
                    k_ptrs + start_n * stride_kn,
                    mask=(start_n + offs_n)[:, None] < seqlen_k,
                    other=0.0,
                )
            else:
                k = tl.load(
                    k_ptrs + start_n * stride_kn,
                    mask=((start_n + offs_n)[:, None] < seqlen_k)
                    & (offs_d[None, :] < headdim),
                    other=0.0,
                )

        # -- compute qk_orig ---
        qk_orig = tl.zeros([BLOCK_M, BLOCK_N], dtype=tl.float32)
        qk_orig += tl.dot(q, tl.trans(k))

        if not EVEN_N:  # Mask out padding tokens
            qk_orig += tl.where((start_n + offs_n)[None, :] < seqlen_k, 0, float("-inf"))
        if IS_CAUSAL:  # Mask out future tokens
            qk_orig += tl.where(
                offs_m[:, None] >= (start_n + offs_n)[None, :], 0, float("-inf")
            )

        # -- compute scores_eff ---
        if BIAS_TYPE != "none":
            if BIAS_TYPE == "vector":
                if EVEN_N:
                    bias = tl.load(b_ptrs + start_n).to(tl.float32)
                else:
                    bias = tl.load(
                        b_ptrs + start_n, mask=(start_n + offs_n) < seqlen_k, other=0.0
                    ).to(tl.float32)
                bias = bias[None, :]
            elif BIAS_TYPE == "matrix":
                if EVEN_M & EVEN_N:
                    bias = tl.load(b_ptrs + start_n).to(tl.float32)
                else:
                    bias = tl.load(
                        b_ptrs + start_n,
                        mask=(offs_m[:, None] < seqlen_q)
                        & ((start_n + offs_n)[None, :] < seqlen_k),
                        other=0.0,
                    ).to(tl.float32)
            scores_eff = qk_orig * softmax_scale + bias
        else:
            scores_eff = qk_orig * softmax_scale

        # -- softpick computation --
        m_ij = tl.maximum(tl.max(scores_eff, 1), max_i)

        exp_scores_minus_mij = tl.exp(scores_eff - m_ij[:, None])
        exp_neg_mij = tl.exp(
            -m_ij[:, None]
        )  # This is exp(-max_effective_score_for_block)
        # Note: og_flashsoftpick used exp(-b_m) where b_m was new max.
        # Here m_ij is the new max.
        exp_diff_terms = exp_scores_minus_mij - exp_neg_mij

        p_num_block = tl.maximum(exp_diff_terms, 0.0)
        # Denominator terms: sum_k abs(exp(s_k - m_ij) - exp(-m_ij))
        # Masking for p_den_terms_abs is implicitly handled by scores_eff being -inf for masked elements,
        # which makes exp_scores_minus_mij zero. Then exp_diff_terms is -exp_neg_mij.
        # abs makes it exp_neg_mij. sum will include these.
        # This is consistent with softpick definition.
        p_den_terms_abs = tl.abs(exp_diff_terms)
        # Explicitly zero out contributions from masked tokens to sum_abs_val_block
        # if not EVEN_N: # Not needed if scores_eff is -inf
        #    p_den_terms_abs = tl.where((start_n + offs_n)[None, :] < seqlen_k, p_den_terms_abs, 0.0)
        # if IS_CAUSAL: # Not needed if scores_eff is -inf
        #    p_den_terms_abs = tl.where(offs_m[:, None] >= (start_n + offs_n)[None, :], p_den_terms_abs, 0.0)

        sum_abs_val_block = tl.sum(p_den_terms_abs, 1)

        # Rescale previous accumulators
        # BUG: have to store and immediately load
        exp_max_diff_scale = tl.exp(max_i - m_ij)
        tl.store(t_ptrs, exp_max_diff_scale)
        exp_max_diff_scale = tl.load(t_ptrs)

        acc_o = acc_o * exp_max_diff_scale[:, None]
        sum_abs_val_i = sum_abs_val_i * exp_max_diff_scale

        # Update accumulators with current block
        sum_abs_val_i += sum_abs_val_block

        # Load V
        if EVEN_N & EVEN_M:
            if EVEN_HEADDIM:
                v = tl.load(v_ptrs + start_n * stride_vn)
            else:
                v = tl.load(
                    v_ptrs + start_n * stride_vn,
                    mask=offs_d[None, :] < headdim,
                    other=0.0,
                )
        else:
            if EVEN_HEADDIM:
                v = tl.load(
                    v_ptrs + start_n * stride_vn,
                    mask=(start_n + offs_n)[:, None] < seqlen_k,
                    other=0.0,
                )
            else:
                v = tl.load(
                    v_ptrs + start_n * stride_vn,
                    mask=((start_n + offs_n)[:, None] < seqlen_k)
                    & (offs_d[None, :] < headdim),
                    other=0.0,
                )
        acc_o += tl.dot(p_num_block.to(v.dtype), v)

        # Update current max
        max_i = m_ij

    # Finalize output and LSE
    sum_abs_val_final_safe = sum_abs_val_i + 1e-6  # Add epsilon for stability

    # Store LSE: max_i + log(sum_abs_val_final_safe)
    lse_ptrs = Lse + off_hb * seqlen_q_rounded + offs_m
    tl.store(lse_ptrs, max_i + tl.log(sum_abs_val_final_safe))

    # Store Output: acc_o / sum_abs_val_final_safe
    # BUG: have to store and immediately load o_scale if it were exp. Here it's division.
    # final_out_scale = 1.0 / sum_abs_val_final_safe # Replaced direct division
    # tl.store(t_ptrs, final_out_scale)
    # final_out_scale = tl.load(t_ptrs)
    # acc_o_final = acc_o * final_out_scale[:, None]
    acc_o_final = acc_o / sum_abs_val_final_safe[:, None]

    # rematerialize offsets to save registers (not needed, already have them)
    # offs_m = start_m * BLOCK_M + tl.arange(0, BLOCK_M)
    offs_d = tl.arange(
        0, BLOCK_HEADDIM
    )  # Re-declare for clarity if registers were an issue
    out_ptrs = (
        Out
        + off_b * stride_ob
        + off_h * stride_oh
        + (offs_m[:, None] * stride_om + offs_d[None, :])
    )

    if EVEN_M:
        if EVEN_HEADDIM:
            tl.store(out_ptrs, acc_o_final)
        else:
            tl.store(out_ptrs, acc_o_final, mask=offs_d[None, :] < headdim)
    else:
        if EVEN_HEADDIM:
            tl.store(out_ptrs, acc_o_final, mask=offs_m[:, None] < seqlen_q)
        else:
            tl.store(
                out_ptrs,
                acc_o_final,
                mask=(offs_m[:, None] < seqlen_q) & (offs_d[None, :] < headdim),
            )


@triton.jit
def _bwd_preprocess_do_o_dot(
    Out,
    DO,
    Delta,
    stride_ob,
    stride_oh,
    stride_om,
    stride_dob,
    stride_doh,
    stride_dom,
    nheads,
    seqlen_q,
    seqlen_q_rounded,
    headdim,
    BLOCK_M: tl.constexpr,
    BLOCK_HEADDIM: tl.constexpr,
):
    """
    _bwd_preprocess_do_o_dot is a Triton implementation of the backward pass of FlashAttention.

    Args:
        Out (torch.Tensor): The output tensor from the forward pass of FlashAttention.
        DO (torch.Tensor): The gradient of the output tensor from the backward pass.
        Delta (torch.Tensor): The tensor to store the sum of element-wise product of Out and DO.
        stride_ob (int): Stride for the batch dimension in the output tensor.
        stride_oh (int): Stride for the head dimension in the output tensor.
        stride_om (int): Stride for the sequence dimension in the output tensor.
        stride_dob (int): Stride for the batch dimension in the DO tensor.
        stride_doh (int): Stride for the head dimension in the DO tensor.
        stride_dom (int): Stride for the sequence dimension in the DO tensor.
        nheads (int): Number of attention heads.
        seqlen_q (int): Sequence length for the query tensor.
        seqlen_q_rounded (int): Rounded up sequence length for the query tensor.
        headdim (int): Dimension of each attention head.
        BLOCK_M (tl.constexpr): Block size for the sequence dimension in the query tensor.
        BLOCK_HEADDIM (tl.constexpr): Block size for the head dimension.
    """
    start_m = tl.program_id(0)
    off_hb = tl.program_id(1)
    off_b = off_hb // nheads
    off_h = off_hb % nheads
    # initialize offsets
    offs_m = start_m * BLOCK_M + tl.arange(0, BLOCK_M)
    offs_d = tl.arange(0, BLOCK_HEADDIM)
    # load
    o = tl.load(
        Out
        + off_b * stride_ob
        + off_h * stride_oh
        + offs_m[:, None] * stride_om
        + offs_d[None, :],
        mask=(offs_m[:, None] < seqlen_q) & (offs_d[None, :] < headdim),
        other=0.0,
    ).to(tl.float32)
    do = tl.load(
        DO
        + off_b * stride_dob
        + off_h * stride_doh
        + offs_m[:, None] * stride_dom
        + offs_d[None, :],
        mask=(offs_m[:, None] < seqlen_q) & (offs_d[None, :] < headdim),
        other=0.0,
    ).to(tl.float32)
    delta = tl.sum(o * do, axis=1)
    # write-back
    tl.store(Delta + off_hb * seqlen_q_rounded + offs_m, delta)


@triton.jit
def _bwd_store_dk_dv(
    dk_ptrs,
    dv_ptrs,
    dk,
    dv,
    offs_n,
    offs_d,
    seqlen_k,
    headdim,
    EVEN_M: tl.constexpr,
    EVEN_N: tl.constexpr,
    EVEN_HEADDIM: tl.constexpr,
):
    # [2022-11-01] TD: Same bug. In the case of EVEN_N=True and EVEN_M=False,
    # if we just call tl.store(dv_ptrs), there's a race condition
    if EVEN_N & EVEN_M:
        if EVEN_HEADDIM:
            tl.store(dv_ptrs, dv)
            tl.store(dk_ptrs, dk)
        else:
            tl.store(dv_ptrs, dv, mask=offs_d[None, :] < headdim)
            tl.store(dk_ptrs, dk, mask=offs_d[None, :] < headdim)
    else:
        if EVEN_HEADDIM:
            tl.store(dv_ptrs, dv, mask=offs_n[:, None] < seqlen_k)
            tl.store(dk_ptrs, dk, mask=offs_n[:, None] < seqlen_k)
        else:
            tl.store(
                dv_ptrs,
                dv,
                mask=(offs_n[:, None] < seqlen_k) & (offs_d[None, :] < headdim),
            )
            tl.store(
                dk_ptrs,
                dk,
                mask=(offs_n[:, None] < seqlen_k) & (offs_d[None, :] < headdim),
            )


@triton.jit
def _bwd_kernel_one_col_block(
    start_n,
    Q,
    K,
    V,
    Bias,
    DO,
    DQ,
    DK,
    DV,
    LSE,
    D,
    softmax_scale,
    stride_qm,
    stride_kn,
    stride_vn,
    stride_bm,
    stride_dom,
    stride_dqm,
    stride_dkn,
    stride_dvn,
    seqlen_q,
    seqlen_k,
    headdim,
    ATOMIC_ADD: tl.constexpr,
    BIAS_TYPE: tl.constexpr,
    IS_CAUSAL: tl.constexpr,
    BLOCK_HEADDIM: tl.constexpr,
    EVEN_M: tl.constexpr,
    EVEN_N: tl.constexpr,
    EVEN_HEADDIM: tl.constexpr,
    BLOCK_M: tl.constexpr,
    BLOCK_N: tl.constexpr,
):
    # We need to make sure begin_m is a multiple of BLOCK_M (not BLOCK_N)
    begin_m = 0 if not IS_CAUSAL else ((start_n * BLOCK_N) // BLOCK_M) * BLOCK_M
    # initialize row/col offsets
    offs_qm = begin_m + tl.arange(0, BLOCK_M)
    offs_n = start_n * BLOCK_N + tl.arange(0, BLOCK_N)
    offs_m = tl.arange(0, BLOCK_M)
    offs_d = tl.arange(0, BLOCK_HEADDIM)
    # initialize pointers to value-like data
    q_ptrs = Q + (offs_qm[:, None] * stride_qm + offs_d[None, :])
    k_ptrs = K + (offs_n[:, None] * stride_kn + offs_d[None, :])
    v_ptrs = V + (offs_n[:, None] * stride_vn + offs_d[None, :])
    do_ptrs = DO + (offs_qm[:, None] * stride_dom + offs_d[None, :])
    dq_ptrs = DQ + (offs_qm[:, None] * stride_dqm + offs_d[None, :])
    if BIAS_TYPE == "vector":
        b_ptrs = Bias + offs_n
    elif BIAS_TYPE == "matrix":
        b_ptrs = Bias + (offs_qm[:, None] * stride_bm + offs_n[None, :])
    # initialize dv and dk
    dv = tl.zeros([BLOCK_N, BLOCK_HEADDIM], dtype=tl.float32)
    dk = tl.zeros([BLOCK_N, BLOCK_HEADDIM], dtype=tl.float32)
    # There seems to be some problem with Triton pipelining that makes results wrong for
    # headdim=64, seqlen=(113, 255), bias_type='matrix'. In this case the for loop
    # may have zero step, and pipelining with the bias matrix could screw it up.
    # So we just exit early.
    if begin_m >= seqlen_q:
        dv_ptrs = DV + (offs_n[:, None] * stride_dvn + offs_d[None, :])
        dk_ptrs = DK + (offs_n[:, None] * stride_dkn + offs_d[None, :])
        _bwd_store_dk_dv(
            dk_ptrs,
            dv_ptrs,
            dk,
            dv,
            offs_n,
            offs_d,
            seqlen_k,
            headdim,
            EVEN_M=EVEN_M,
            EVEN_N=EVEN_N,
            EVEN_HEADDIM=EVEN_HEADDIM,
        )
        return
    # k and v stay in SRAM throughout
    # [2022-10-30] TD: Same bug as the fwd. In the case of EVEN_N=True and EVEN_M=False,
    # if we just call tl.load(k_ptrs), we get the wrong output!
    if EVEN_N & EVEN_M:
        if EVEN_HEADDIM:
            k = tl.load(k_ptrs)
            v = tl.load(v_ptrs)
        else:
            k = tl.load(k_ptrs, mask=offs_d[None, :] < headdim, other=0.0)
            v = tl.load(v_ptrs, mask=offs_d[None, :] < headdim, other=0.0)
    else:
        if EVEN_HEADDIM:
            k = tl.load(k_ptrs, mask=offs_n[:, None] < seqlen_k, other=0.0)
            v = tl.load(v_ptrs, mask=offs_n[:, None] < seqlen_k, other=0.0)
        else:
            k = tl.load(
                k_ptrs,
                mask=(offs_n[:, None] < seqlen_k) & (offs_d[None, :] < headdim),
                other=0.0,
            )
            v = tl.load(
                v_ptrs,
                mask=(offs_n[:, None] < seqlen_k) & (offs_d[None, :] < headdim),
                other=0.0,
            )
    # loop over rows
    num_block_m = tl.cdiv(seqlen_q, BLOCK_M)
    for start_m in range(begin_m, num_block_m * BLOCK_M, BLOCK_M):
        start_m = tl.multiple_of(start_m, BLOCK_M)
        offs_m_curr = start_m + offs_m
        # load q, k, v, do on-chip
        if EVEN_M & EVEN_HEADDIM:
            q = tl.load(q_ptrs)
        else:
            if EVEN_HEADDIM:
                q = tl.load(q_ptrs, mask=offs_m_curr[:, None] < seqlen_q, other=0.0)
            else:
                q = tl.load(
                    q_ptrs,
                    mask=(offs_m_curr[:, None] < seqlen_q) & (offs_d[None, :] < headdim),
                    other=0.0,
                )

        # recompute scores_eff = qk_orig * softmax_scale (+ bias)
        qk_orig = tl.dot(q, tl.trans(k))
        # Apply masks consistent with forward
        if not EVEN_N:
            qk_orig = tl.where(offs_n[None, :] < seqlen_k, qk_orig, float("-inf"))
        if IS_CAUSAL:
            qk_orig = tl.where(
                offs_m_curr[:, None] >= (offs_n[None, :]), qk_orig, float("-inf")
            )

        if BIAS_TYPE != "none":
            tl.debug_barrier()
            if BIAS_TYPE == "vector":
                if EVEN_N:
                    bias = tl.load(b_ptrs).to(tl.float32)
                else:
                    bias = tl.load(b_ptrs, mask=offs_n < seqlen_k, other=0.0).to(
                        tl.float32
                    )
                bias = bias[None, :]
            elif BIAS_TYPE == "matrix":
                if EVEN_M & EVEN_N:
                    bias = tl.load(b_ptrs).to(tl.float32)
                else:
                    bias = tl.load(
                        b_ptrs,
                        mask=(offs_m_curr[:, None] < seqlen_q)
                        & (offs_n[None, :] < seqlen_k),
                        other=0.0,
                    ).to(tl.float32)
            scores_eff = qk_orig * softmax_scale + bias
        else:
            scores_eff = qk_orig * softmax_scale

        if not (EVEN_M & EVEN_HEADDIM):  # Barrier from original code
            tl.debug_barrier()

        lse_i = tl.load(LSE + offs_m_curr)  # This is max_final + log(sum_abs_final)
        Di = tl.load(D + offs_m_curr)  # This is sum(o * do)

        # Load dO
        if EVEN_M & EVEN_HEADDIM:
            do = tl.load(do_ptrs)
        else:
            do = tl.load(
                do_ptrs,
                mask=(offs_m_curr[:, None] < seqlen_q) & (offs_d[None, :] < headdim),
                other=0.0,
            )

        # --- Softpick backward pass ---
        # 1. Compute P_softpick_terms for dV
        # X_over_D_terms = exp(scores_eff - lse_i[:,None]) - exp(-lse_i[:,None]) -> this is (exp(s-m)-exp(-m))/D
        # lse_i contains m, so exp(-lse_i) is exp(-(m+logD)) = exp(-m)/D
        # exp(scores_eff - lse_i[:,None]) is exp(s-(m+logD)) = exp(s-m)/D
        X_over_D_terms = tl.exp(scores_eff - lse_i[:, None]) - tl.exp(-lse_i[:, None])
        P_softpick_terms = tl.maximum(X_over_D_terms, 0.0)

        # Mask P_softpick_terms consistent with forward pass logic for scores_eff
        # (already handled if scores_eff is -inf for masked parts, making X_over_D_terms negative or zero pre-relu)
        # Example explicit masking (if needed, though scores_eff should handle it):
        # if not EVEN_N:
        #    P_softpick_terms = tl.where(offs_n[None, :] < seqlen_k, P_softpick_terms, 0.0)
        # if IS_CAUSAL:
        #    P_softpick_terms = tl.where(offs_m_curr[:, None] >= (offs_n[None, :]), P_softpick_terms, 0.0)

        dv += tl.dot(tl.trans(P_softpick_terms.to(do.dtype)), do)

        # 2. Compute ds (dL/d(qk_orig)) for dQ, dK
        # dp = dot(v, do) or dot(do, v.T)
        # Barrier from original
        if not (EVEN_M & EVEN_HEADDIM):
            tl.debug_barrier()
        dp = tl.dot(do, tl.trans(v))
        if not EVEN_HEADDIM:  # Barrier from original
            tl.debug_barrier()

        # p_scaled_exp_div_sum_abs = exp(scores_eff - lse_i[:,None]) -> exp(s-m)/D
        p_scaled_exp_div_sum_abs = tl.exp(scores_eff - lse_i[:, None])

        # Conditions based on scores_eff > 0 (as in og_flashsoftpick)
        ds_intermediate_term = tl.where(scores_eff > 0, dp, 0.0)
        ds_delta_term = tl.where(scores_eff > 0, Di[:, None], -Di[:, None])

        ds_wrt_scores_eff = p_scaled_exp_div_sum_abs * (
            ds_intermediate_term - ds_delta_term
        )
        # ds is dL/d(qk_orig), so multiply by softmax_scale
        ds = (ds_wrt_scores_eff * softmax_scale).to(q.dtype)

        # compute dk = dot(ds.T, q)
        dk += tl.dot(tl.trans(ds), q)  # q is unscaled here.

        # compute dq
        if not (EVEN_M & EVEN_HEADDIM):
            tl.debug_barrier()
        if not ATOMIC_ADD:
            if EVEN_M & EVEN_HEADDIM:
                dq_old = tl.load(dq_ptrs, eviction_policy="evict_last")
                dq_old += tl.dot(ds, k)  # k is unscaled here.
                tl.store(dq_ptrs, dq_old, eviction_policy="evict_last")
            else:
                # (Masked load, add, store for dq)
                if EVEN_HEADDIM:
                    dq_old = tl.load(
                        dq_ptrs,
                        mask=offs_m_curr[:, None] < seqlen_q,
                        other=0.0,
                        eviction_policy="evict_last",
                    )
                    dq_old += tl.dot(ds, k)
                    tl.store(
                        dq_ptrs,
                        dq_old,
                        mask=offs_m_curr[:, None] < seqlen_q,
                        eviction_policy="evict_last",
                    )
                else:
                    dq_old = tl.load(
                        dq_ptrs,
                        mask=(offs_m_curr[:, None] < seqlen_q)
                        & (offs_d[None, :] < headdim),
                        other=0.0,
                        eviction_policy="evict_last",
                    )
                    dq_old += tl.dot(ds, k)
                    tl.store(
                        dq_ptrs,
                        dq_old,
                        mask=(offs_m_curr[:, None] < seqlen_q)
                        & (offs_d[None, :] < headdim),
                        eviction_policy="evict_last",
                    )
        else:  # SEQUENCE_PARALLEL, use atomic add for dq
            dq_new = tl.dot(ds, k)
            if EVEN_M & EVEN_HEADDIM:
                tl.atomic_add(dq_ptrs, dq_new)
            else:
                if EVEN_HEADDIM:
                    tl.atomic_add(dq_ptrs, dq_new, mask=offs_m_curr[:, None] < seqlen_q)
                else:
                    tl.atomic_add(
                        dq_ptrs,
                        dq_new,
                        mask=(offs_m_curr[:, None] < seqlen_q)
                        & (offs_d[None, :] < headdim),
                    )
        # increment pointers
        dq_ptrs += BLOCK_M * stride_dqm
        q_ptrs += BLOCK_M * stride_qm
        do_ptrs += BLOCK_M * stride_dom
        if BIAS_TYPE == "matrix":
            b_ptrs += BLOCK_M * stride_bm
    # write-back
    dv_ptrs = DV + (offs_n[:, None] * stride_dvn + offs_d[None, :])
    dk_ptrs = DK + (offs_n[:, None] * stride_dkn + offs_d[None, :])
    _bwd_store_dk_dv(
        dk_ptrs,
        dv_ptrs,
        dk,
        dv,
        offs_n,
        offs_d,
        seqlen_k,
        headdim,
        EVEN_M=EVEN_M,
        EVEN_N=EVEN_N,
        EVEN_HEADDIM=EVEN_HEADDIM,
    )


def init_to_zero(name):
    return lambda nargs: nargs[name].zero_()


@triton.autotune(
    configs=[
        triton.Config(
            {"BLOCK_M": 128, "BLOCK_N": 128, "SEQUENCE_PARALLEL": False},
            num_warps=8,
            num_stages=1,
            pre_hook=init_to_zero("DQ"),
        ),
        triton.Config(
            {"BLOCK_M": 128, "BLOCK_N": 128, "SEQUENCE_PARALLEL": True},
            num_warps=8,
            num_stages=1,
            pre_hook=init_to_zero("DQ"),
        ),
        # Other configs seem to give wrong results when seqlen_q % 128 != 0, disabling them for now
        # # Kernel is buggy (give wrong result) if we set BLOCK_m=128, BLOCK_n=64, num_warps=*4*
        # triton.Config({"BLOCK_M": 128, "BLOCK_N": 64, "SEQUENCE_PARALLEL": False}, num_warps=8, num_stages=1, pre_hook=init_to_zero('DQ')),
        # triton.Config({"BLOCK_M": 128, "BLOCK_N": 64, "SEQUENCE_PARALLEL": True}, num_warps=8, num_stages=1, pre_hook=init_to_zero('DQ')),
        # triton.Config({"BLOCK_M": 64, "BLOCK_N": 64, "SEQUENCE_PARALLEL": False}, num_warps=4, num_stages=1, pre_hook=init_to_zero('DQ')),
        # triton.Config({"BLOCK_M": 64, "BLOCK_N": 64, "SEQUENCE_PARALLEL": True}, num_warps=4, num_stages=1, pre_hook=init_to_zero('DQ')),
    ],
    key=[
        "CACHE_KEY_SEQLEN_Q",
        "CACHE_KEY_SEQLEN_K",
        "BIAS_TYPE",
        "IS_CAUSAL",
        "BLOCK_HEADDIM",
    ],
)
@triton.heuristics(
    {
        "EVEN_M": lambda args: args["seqlen_q"] % args["BLOCK_M"] == 0,
        "EVEN_N": lambda args: args["seqlen_k"] % args["BLOCK_N"] == 0,
        "EVEN_HEADDIM": lambda args: args["headdim"] == args["BLOCK_HEADDIM"],
    }
)
@triton.jit
def _bwd_kernel(
    Q,
    K,
    V,
    Bias,
    DO,
    DQ,
    DK,
    DV,
    LSE,
    D,
    softmax_scale,
    stride_qb,
    stride_qh,
    stride_qm,
    stride_kb,
    stride_kh,
    stride_kn,
    stride_vb,
    stride_vh,
    stride_vn,
    stride_bb,
    stride_bh,
    stride_bm,
    stride_dob,
    stride_doh,
    stride_dom,
    stride_dqb,
    stride_dqh,
    stride_dqm,
    stride_dkb,
    stride_dkh,
    stride_dkn,
    stride_dvb,
    stride_dvh,
    stride_dvn,
    nheads,
    seqlen_q,
    seqlen_k,
    seqlen_q_rounded,
    headdim,
    CACHE_KEY_SEQLEN_Q,
    CACHE_KEY_SEQLEN_K,
    BIAS_TYPE: tl.constexpr,
    IS_CAUSAL: tl.constexpr,
    BLOCK_HEADDIM: tl.constexpr,
    SEQUENCE_PARALLEL: tl.constexpr,
    EVEN_M: tl.constexpr,
    EVEN_N: tl.constexpr,
    EVEN_HEADDIM: tl.constexpr,
    BLOCK_M: tl.constexpr,
    BLOCK_N: tl.constexpr,
):
    off_hb = tl.program_id(1)
    off_b = off_hb // nheads
    off_h = off_hb % nheads
    # offset pointers for batch/head
    Q += off_b * stride_qb + off_h * stride_qh
    K += off_b * stride_kb + off_h * stride_kh
    V += off_b * stride_vb + off_h * stride_vh
    DO += off_b * stride_dob + off_h * stride_doh
    DQ += off_b * stride_dqb + off_h * stride_dqh
    DK += off_b * stride_dkb + off_h * stride_dkh
    DV += off_b * stride_dvb + off_h * stride_dvh
    if BIAS_TYPE != "none":
        Bias += off_b * stride_bb + off_h * stride_bh
    # pointer to row-wise quantities in value-like data
    D += off_hb * seqlen_q_rounded
    LSE += off_hb * seqlen_q_rounded
    if not SEQUENCE_PARALLEL:
        num_block_n = tl.cdiv(seqlen_k, BLOCK_N)
        for start_n in range(0, num_block_n):
            _bwd_kernel_one_col_block(
                start_n,
                Q,
                K,
                V,
                Bias,
                DO,
                DQ,
                DK,
                DV,
                LSE,
                D,
                softmax_scale,
                stride_qm,
                stride_kn,
                stride_vn,
                stride_bm,
                stride_dom,
                stride_dqm,
                stride_dkn,
                stride_dvn,
                seqlen_q,
                seqlen_k,
                headdim,
                ATOMIC_ADD=False,
                BIAS_TYPE=BIAS_TYPE,
                IS_CAUSAL=IS_CAUSAL,
                BLOCK_HEADDIM=BLOCK_HEADDIM,
                EVEN_M=EVEN_M,
                EVEN_N=EVEN_N,
                EVEN_HEADDIM=EVEN_HEADDIM,
                BLOCK_M=BLOCK_M,
                BLOCK_N=BLOCK_N,
            )
    else:
        start_n = tl.program_id(0)
        _bwd_kernel_one_col_block(
            start_n,
            Q,
            K,
            V,
            Bias,
            DO,
            DQ,
            DK,
            DV,
            LSE,
            D,
            softmax_scale,
            stride_qm,
            stride_kn,
            stride_vn,
            stride_bm,
            stride_dom,
            stride_dqm,
            stride_dkn,
            stride_dvn,
            seqlen_q,
            seqlen_k,
            headdim,
            ATOMIC_ADD=True,
            BIAS_TYPE=BIAS_TYPE,
            IS_CAUSAL=IS_CAUSAL,
            BLOCK_HEADDIM=BLOCK_HEADDIM,
            EVEN_M=EVEN_M,
            EVEN_N=EVEN_N,
            EVEN_HEADDIM=EVEN_HEADDIM,
            BLOCK_M=BLOCK_M,
            BLOCK_N=BLOCK_N,
        )


def _flash_attn_forward(
    q: torch.Tensor,
    k: torch.Tensor,
    v: torch.Tensor,
    bias: torch.Tensor | None = None,
    causal: bool = False,
    softmax_scale: float | None = None,
) -> torch.Tensor:
    """
    Perform the forward pass of FlashAttention.

    Args:
        q (torch.Tensor): Query tensor of shape (batch, seqlen_q, nheads, d).
        k (torch.Tensor): Key tensor of shape (batch, seqlen_k, nheads, d).
        v (torch.Tensor): Value tensor of shape (batch, seqlen_k, nheads, d).
        bias (Optional[torch.Tensor]): Bias tensor of shape (batch, nheads, seqlen_q, seqlen_k) or (batch, nheads, 1, seqlen_k). Default is None.
        causal (bool): Whether to apply causal masking. Default is False.
        softmax_scale (Optional[float]): Scaling factor for the softmax operation. Default is None.

    Returns
    -------
        torch.Tensor: Output tensor of the same shape as the query tensor.
    """
    # shape constraints
    batch, seqlen_q, _, d = q.shape
    _, seqlen_k, nheads, _ = k.shape
    assert k.shape == (batch, seqlen_k, nheads, d)
    assert v.shape == (batch, seqlen_k, nheads, d)
    assert d <= 128, "FlashAttention only support head dimensions up to 128"
    assert q.dtype == k.dtype == v.dtype, "All tensors must have the same type"
    assert q.dtype in [torch.float16, torch.bfloat16], "Only support fp16 and bf16"
    assert q.is_cuda and k.is_cuda and v.is_cuda
    softmax_scale = softmax_scale or 1.0 / math.sqrt(d)

    has_bias = bias is not None
    bias_type = "none"
    if has_bias:
        assert bias.dtype in [q.dtype, torch.float]
        assert bias.is_cuda
        assert bias.dim() == 4
        if bias.stride(-1) != 1:
            bias = bias.contiguous()
        if bias.shape[2:] == (1, seqlen_k):
            bias_type = "vector"
        elif bias.shape[2:] == (seqlen_q, seqlen_k):
            bias_type = "matrix"
        else:
            raise RuntimeError(
                "Last 2 dimensions of bias must be (1, seqlen_k) or (seqlen_q, seqlen_k)"
            )
        bias = bias.expand(batch, nheads, seqlen_q, seqlen_k)
    bias_strides = (
        (bias.stride(0), bias.stride(1), bias.stride(2)) if has_bias else (0, 0, 0)
    )

    seqlen_q_rounded = math.ceil(seqlen_q / 128) * 128
    lse = torch.empty(
        (batch, nheads, seqlen_q_rounded), device=q.device, dtype=torch.float32
    )
    tmp = torch.empty(
        (batch, nheads, seqlen_q_rounded), device=q.device, dtype=torch.float32
    )
    o = torch.empty_like(q)

    BLOCK_HEADDIM = max(triton.next_power_of_2(d), 16)
    BLOCK = 128
    num_warps = 4 if d <= 64 else 8
    grid = lambda META: (triton.cdiv(seqlen_q, META["BLOCK_M"]), batch * nheads)
    _fwd_kernel[grid](
        q,
        k,
        v,
        bias,
        o,
        lse,
        tmp,
        softmax_scale,
        q.stride(0),
        q.stride(2),
        q.stride(1),
        k.stride(0),
        k.stride(2),
        k.stride(1),
        v.stride(0),
        v.stride(2),
        v.stride(1),
        *bias_strides,
        o.stride(0),
        o.stride(2),
        o.stride(1),
        nheads,
        seqlen_q,
        seqlen_k,
        seqlen_q_rounded,
        d,
        seqlen_q // 32,
        seqlen_k // 32,  # key for triton cache (limit number of compilations)
        # Can't use kwargs here because triton autotune expects key to be args, not kwargs
        # IS_CAUSAL=causal, BLOCK_HEADDIM=d,
        bias_type,
        causal,
        BLOCK_HEADDIM,
        BLOCK_M=BLOCK,
        BLOCK_N=BLOCK,
        num_warps=num_warps,
        num_stages=1,
    )
    return o, lse, softmax_scale  # softmax_scale could have been updated


def _flash_attn_backward(
    do, q, k, v, o, lse, dq, dk, dv, bias=None, causal=False, softmax_scale=None
):
    # Make sure that the last dimension is contiguous
    if do.stride(-1) != 1:
        do = do.contiguous()
    batch, seqlen_q, nheads, d = q.shape
    _, seqlen_k, _, _ = k.shape
    # assert d in {16, 32, 64, 128}
    assert d <= 128
    seqlen_q_rounded = math.ceil(seqlen_q / 128) * 128
    assert lse.shape == (batch, nheads, seqlen_q_rounded)
    assert q.stride(-1) == k.stride(-1) == v.stride(-1) == o.stride(-1) == 1
    assert dq.stride(-1) == dk.stride(-1) == dv.stride(-1) == 1
    softmax_scale = softmax_scale or 1.0 / math.sqrt(d)
    # dq_accum = torch.zeros_like(q, dtype=torch.float32)
    dq_accum = torch.empty_like(q, dtype=torch.float32)
    delta = torch.empty_like(lse)
    # delta = torch.zeros_like(lse)

    BLOCK_HEADDIM = max(triton.next_power_of_2(d), 16)
    grid = lambda META: (triton.cdiv(seqlen_q, META["BLOCK_M"]), batch * nheads)
    _bwd_preprocess_do_o_dot[grid](
        o,
        do,
        delta,
        o.stride(0),
        o.stride(2),
        o.stride(1),
        do.stride(0),
        do.stride(2),
        do.stride(1),
        nheads,
        seqlen_q,
        seqlen_q_rounded,
        d,
        BLOCK_M=128,
        BLOCK_HEADDIM=BLOCK_HEADDIM,
    )

    has_bias = bias is not None
    bias_type = "none"
    if has_bias:
        assert bias.dtype in [q.dtype, torch.float]
        assert bias.is_cuda
        assert bias.dim() == 4
        assert bias.stride(-1) == 1
        if bias.shape[2:] == (1, seqlen_k):
            bias_type = "vector"
        elif bias.shape[2:] == (seqlen_q, seqlen_k):
            bias_type = "matrix"
        else:
            raise RuntimeError(
                "Last 2 dimensions of bias must be (1, seqlen_k) or (seqlen_q, seqlen_k)"
            )
        bias = bias.expand(batch, nheads, seqlen_q, seqlen_k)
    bias_strides = (
        (bias.stride(0), bias.stride(1), bias.stride(2)) if has_bias else (0, 0, 0)
    )

    # BLOCK_M = 128
    # BLOCK_N = 64
    # num_warps = 4
    grid = lambda META: (
        triton.cdiv(seqlen_k, META["BLOCK_N"]) if META["SEQUENCE_PARALLEL"] else 1,
        batch * nheads,
    )
    _bwd_kernel[grid](
        q,
        k,
        v,
        bias,
        do,
        dq_accum,
        dk,
        dv,
        lse,
        delta,
        softmax_scale,
        q.stride(0),
        q.stride(2),
        q.stride(1),
        k.stride(0),
        k.stride(2),
        k.stride(1),
        v.stride(0),
        v.stride(2),
        v.stride(1),
        *bias_strides,
        do.stride(0),
        do.stride(2),
        do.stride(1),
        dq_accum.stride(0),
        dq_accum.stride(2),
        dq_accum.stride(1),
        dk.stride(0),
        dk.stride(2),
        dk.stride(1),
        dv.stride(0),
        dv.stride(2),
        dv.stride(1),
        nheads,
        seqlen_q,
        seqlen_k,
        seqlen_q_rounded,
        d,
        seqlen_q // 32,
        seqlen_k // 32,  # key for triton cache (limit number of compilations)
        # Can't use kwargs here because triton autotune expects key to be args, not kwargs
        # IS_CAUSAL=causal, BLOCK_HEADDIM=d,
        bias_type,
        causal,
        BLOCK_HEADDIM,
        # SEQUENCE_PARALLEL=False,
        # BLOCK_M=BLOCK_M, BLOCK_N=BLOCK_N,
        # num_warps=num_warps,
        # num_stages=1,
    )
    dq.copy_(dq_accum)


class FlashAttnQKVPackedFunc(torch.autograd.Function):
    @staticmethod
    def forward(
        ctx: torch.autograd.Function,
        qkv: torch.Tensor,
        bias: torch.Tensor | None = None,
        causal: bool = False,
        softmax_scale: float | None = None,
    ) -> torch.Tensor:
        """
        Forward pass for FlashAttention.

        Args:
            ctx (torch.autograd.Function): The context object to save information for backward computation.
            qkv (torch.Tensor): Input tensor of shape (batch, seqlen, 3, nheads, headdim).
            bias (Optional[torch.Tensor]): Optional bias tensor, shape broadcastible to (batch, nheads, seqlen, seqlen).
                For example, ALiBi mask for causal would have shape (1, nheads, 1, seqlen).
                ALiBi mask for non-causal would have shape (1, nheads, seqlen, seqlen).
            causal (bool): Whether to apply causal masking. Default is False.
            softmax_scale (Optional[float]): Optional scaling factor for softmax. Default is None.

        Returns
        -------
            torch.Tensor: Output tensor after applying FlashAttention.
        """
        # Make sure that the last dimension is contiguous
        if qkv.stride(-1) != 1:
            qkv = qkv.contiguous()
        o, lse, ctx.softmax_scale = _flash_attn_forward(
            qkv[:, :, 0],
            qkv[:, :, 1],
            qkv[:, :, 2],
            bias=bias,
            causal=causal,
            softmax_scale=softmax_scale,
        )
        ctx.save_for_backward(qkv, o, lse, bias)
        ctx.causal = causal
        return o

    @staticmethod
    def backward(ctx, do):
        qkv, o, lse, bias = ctx.saved_tensors
        assert not ctx.needs_input_grad[
            1
        ], "FlashAttention does not support bias gradient yet"
        # Triton's autotune causes the Tensor._version to change, and so Pytorch autograd
        # does a memcpy. To avoid this we run in inference_mode, which doesn't track the version.
        with torch.inference_mode():
            dqkv = torch.empty_like(qkv)
            _flash_attn_backward(
                do,
                qkv[:, :, 0],
                qkv[:, :, 1],
                qkv[:, :, 2],
                o,
                lse,
                dqkv[:, :, 0],
                dqkv[:, :, 1],
                dqkv[:, :, 2],
                bias=bias,
                causal=ctx.causal,
                softmax_scale=ctx.softmax_scale,
            )
        return dqkv, None, None, None


flash_pick_attn_qkvpacked_func = FlashAttnQKVPackedFunc.apply


class FlashAttnKVPackedFunc(torch.autograd.Function):
    @staticmethod
    def forward(
        ctx,
        q: torch.Tensor,
        kv: torch.Tensor,
        bias: torch.Tensor | None = None,
        causal: bool = False,
        softmax_scale: float | None = None,
    ) -> torch.Tensor:
        """
        Perform the forward pass of FlashAttention with packed key and value tensors.

        Args:
            q (torch.Tensor): Query tensor of shape (batch, seqlen_q, nheads, headdim).
            kv (torch.Tensor): Key and value tensor of shape (batch, seqlen_k, 2, nheads, headdim).
            bias (Optional[torch.Tensor]): Bias tensor, shape broadcastable to (batch, nheads, seqlen_q, seqlen_k).
                For example, ALiBi mask for causal would have shape (1, nheads, 1, seqlen_k).
                ALiBi mask for non-causal would have shape (1, nheads, seqlen_q, seqlen_k).
            causal (bool): Whether to apply causal masking. Default is False.
            softmax_scale (Optional[float]): Scaling factor for the softmax operation. Default is None.

        Returns
        -------
            torch.Tensor: Output tensor after applying FlashAttention.
        """
        # Make sure that the last dimension is contiguous
        q, kv = [x if x.stride(-1) == 1 else x.contiguous() for x in [q, kv]]
        o, lse, ctx.softmax_scale = _flash_attn_forward(
            q,
            kv[:, :, 0],
            kv[:, :, 1],
            bias=bias,
            causal=causal,
            softmax_scale=softmax_scale,
        )
        ctx.save_for_backward(q, kv, o, lse, bias)
        ctx.causal = causal
        return o

    @staticmethod
    def backward(ctx, do):
        q, kv, o, lse, bias = ctx.saved_tensors
        if len(ctx.needs_input_grad) >= 3:
            assert not ctx.needs_input_grad[
                2
            ], "FlashAttention does not support bias gradient yet"
        # Triton's autotune causes the Tensor._version to change, and so Pytorch autograd
        # does a memcpy. To avoid this we run in inference_mode, which doesn't track the version.
        with torch.inference_mode():
            dq = torch.empty_like(q)
            dkv = torch.empty_like(kv)
            _flash_attn_backward(
                do,
                q,
                kv[:, :, 0],
                kv[:, :, 1],
                o,
                lse,
                dq,
                dkv[:, :, 0],
                dkv[:, :, 1],
                bias=bias,
                causal=ctx.causal,
                softmax_scale=ctx.softmax_scale,
            )
        return dq, dkv, None, None, None


flash_pick_attn_kvpacked_func = FlashAttnKVPackedFunc.apply
