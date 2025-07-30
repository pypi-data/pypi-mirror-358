# Copyright (c) 2023, Tri Dao.

import math
from functools import partial
from typing import Any

import torch
import torch.nn as nn
from einops import rearrange, repeat

from .hyper_attention import HyperAttention

try:
    from .flashattention import (
        flash_attn_kvpacked_func,
        flash_attn_qkvpacked_func,
    )
    from .flashpickattention import (
        flash_pick_attn_kvpacked_func,
        flash_pick_attn_qkvpacked_func,
    )

except ModuleNotFoundError as e:
    print(e)
    print("FlashAttention is not installed, not using it..")
    # raise ValueError("FlashAttention is not installed, not using it..") from e
    flash_attn_kvpacked_func = None
    flash_attn_qkvpacked_func = None
    flash_pick_attn_qkvpacked_func = None
    flash_pick_attn_kvpacked_func = None

# from .flashattention_triton import attention as triton_attention

flash_attn_varlen_kvpacked_func = None
flash_attn_varlen_qkvpacked_func = None
flash_attn_with_kvcache = None
FusedDense = None
RotaryEmbedding = None


class HyperSelfAttention(nn.Module):
    def __init__(
        self,
        causal: bool = False,
        softmax_scale: float | None = None,
        attention_dropout: float = 0.0,
        head_dim: int = 64,
        lsh_num_projs: int = 8,
        block_size: int = 128,
    ):
        super().__init__()
        self.causal = causal
        self.hyper_attention = HyperAttention(
            input_dim=head_dim,
            lsh_num_projs=lsh_num_projs,
            block_size=block_size,
            sample_size=128,
            min_seq_len=2400,
            smooth_block=True,
        )

    def forward(self, qkv, bias=None):
        q, k, v = qkv[:, :, 0, :, :], qkv[:, :, 1, :, :], qkv[:, :, 2, :, :]
        return self.hyper_attention(q, k, v)


class HyperCrossAttention(nn.Module):
    def __init__(
        self,
        causal: bool = False,
        softmax_scale: float | None = None,
        attention_dropout: float = 0.0,
        head_dim: int = 64,
        lsh_num_projs: int = 8,
        block_size: int = 128,
    ):
        super().__init__()
        self.hyper_attention = HyperAttention(
            input_dim=head_dim,
            lsh_num_projs=lsh_num_projs,
            block_size=block_size,
            sample_size=128,
            min_seq_len=4800,
            smooth_block=True,
        )

    def forward(self, q, kv, bias=None):
        k, v = kv[:, :, 0, :, :], kv[:, :, 1, :, :]
        return self.hyper_attention(q, k, v)


class FlashSelfAttention(nn.Module):
    def __init__(
        self,
        causal: bool = False,
        softmax_scale: float | None = None,
        attention_dropout: float = 0.0,
        alibi_slopes: Any | None = None,
        deterministic: bool = False,
        use_triton: bool = True,
        softpick: bool = False,
    ):
        """Implement the scaled dot product attention with softmax.

        Args:
            softmax_scale (float, optional): The temperature to use for the softmax attention.
                (default: 1/sqrt(d_keys) where d_keys is computed at
                runtime)
            attention_dropout (float, optional): The dropout rate to apply to the attention
                (default: 0.0)
            causal (bool, optional): Whether to use causal attention. Defaults to False.
            softpick (bool, optional): Whether to use softpick. Defaults to True.
        """
        super().__init__()
        if flash_attn_qkvpacked_func is None:
            print("FlashAttention is not installed, using triton instead")
            use_triton = True
        self.use_triton = use_triton
        self.attention_dropout = attention_dropout
        self.causal = causal
        self.softmax_scale = softmax_scale
        self.softpick = softpick

    def forward(
        self,
        qkv: torch.Tensor,
        causal: bool | None = None,
        cu_seqlens: torch.Tensor | None = None,
        max_seqlen: int | None = None,
        cu_seqlens_k: torch.Tensor | None = None,
        max_seqlen_k: int | None = None,
        bias: torch.Tensor | None = None,
        **kwargs,
    ):
        """Implements the multihead softmax attention.

        Args
            qkv (Tensor): The tensor containing the query, key, and value.
                If cu_seqlens is None and max_seqlen is None, then qkv has shape (B, S, 3, H, D).
                If cu_seqlens is not None and max_seqlen is not None, then qkv has shape
                (total, 3, H, D), where total is the sum of the sequence lengths in the batch.
            causal (bool): if passed, will override self.causal
            cu_seqlens (batch_size + 1,), dtype torch.int32. The cumulative sequence lengths
                of the sequences in the batch, used to index into qkv.
            max_seqlen (int). Maximum sequence length in the batch.

        Returns
        -------
            out: (total, H, D) if cu_seqlens is not None and max_seqlen is not None,
                else (B, S, H, D).
        """
        assert qkv.dtype in [torch.float16, torch.bfloat16]
        assert qkv.is_cuda
        causal = self.causal if causal is None else causal
        if not self.use_triton:
            raise NotImplementedError("OpenAI's flashattention is not implemented")
            # if qkv.stride(-1) != 1:
            #    qkv = qkv.contiguous()
        else:
            if self.softpick:
                return flash_pick_attn_qkvpacked_func(
                    qkv,
                    bias,
                    # self.drop.p if self.training else 0.0,
                    causal,
                    self.softmax_scale,
                )
            else:
                return flash_attn_qkvpacked_func(
                    qkv,
                    bias,
                    causal,
                    self.softmax_scale,
                    # self.attention_dropout,
                )


class FlashCrossAttention(nn.Module):
    def __init__(
        self,
        causal=False,
        softmax_scale=None,
        attention_dropout=0.0,
        alibi_slopes=None,
        deterministic=False,
        use_triton: bool = True,
        softpick: bool = False,
    ):
        """
        Implement the scaled dot product attention with softmax.

        Args
            softmax_scale: The temperature to use for the softmax attention.
                (default: 1/sqrt(d_keys) where d_keys is computed at
                runtime)
            attention_dropout: The dropout rate to apply to the attention
                (default: 0.0)
        """
        super().__init__()
        assert flash_attn_kvpacked_func is not None, "FlashAttention is not installed"
        assert flash_attn_kvpacked_func is not None, "FlashAttention is not installed"
        self.causal = causal
        self.softmax_scale = softmax_scale
        self.drop = nn.Dropout(attention_dropout)
        self.register_buffer("alibi_slopes", alibi_slopes, persistent=False)
        self.deterministic = deterministic
        self.use_triton = use_triton
        self.softpick = softpick
        self.attention_dropout = attention_dropout

    def forward(
        self,
        q,
        kv,
        causal=None,
        cu_seqlens=None,
        max_seqlen=None,
        cu_seqlens_k=None,
        max_seqlen_k=None,
    ):
        """
        Implements the multihead softmax attention.

        Args
            q: The tensor containing the query. (B, Sq, H, D)
            kv: The tensor containing the key and value. (B, Sk, 2, H_k, D)
            causal: if passed, will override self.causal
            cu_seqlens: (batch_size + 1,), dtype torch.int32. The cumulative sequence lengths
                of the sequences in the batch, used to index into q.
            max_seqlen: int. Maximum sequence length in the batch of q.
            cu_seqlens_k: (batch_size + 1,), dtype torch.int32. The cumulative sequence lengths
                of the sequences in the batch, used to index into kv.
            max_seqlen_k: int. Maximum sequence length in the batch of k and v.
        """
        # Add debug prints
        assert q.dtype in [torch.float16, torch.bfloat16]
        assert q.is_cuda and kv.is_cuda
        causal = self.causal if causal is None else causal
        batch_size, _ = q.shape[0], q.shape[1]
        assert kv.shape[0] == batch_size and kv.shape[4] == q.shape[3]
        # Add GQA support similar to CrossAttention
        if kv.shape[3] != q.shape[2]:  # MQA/GQA
            kv = repeat(kv, "... hkv d -> ... (hkv g) d", g=q.shape[2] // kv.shape[3])

        if self.softpick:
            return flash_pick_attn_kvpacked_func(
                q,
                kv,
                None,
                # self.drop.p if self.training else 0.0,
                causal,
                self.softmax_scale,
                # alibi_slopes=self.alibi_slopes,
                # deterministic=self.deterministic,
            )
        else:
            return flash_attn_kvpacked_func(
                q,
                kv,
                None,
                causal,
                self.softmax_scale,
                # self.attention_dropout,
            )


class SelfAttention(nn.Module):
    """
    Implement the scaled dot product attention with softmax.

    Args:
        softmax_scale: The temperature to use for the softmax attention.
            (default: 1/sqrt(d_keys) where d_keys is computed at
            runtime)
        attention_dropout: The dropout rate to apply to the attention
            (default: 0.0)
        softpick: Whether to use softpick. Defaults to True.
    """

    def __init__(
        self,
        causal=False,
        softmax_scale=None,
        attention_dropout=0.0,
        softpick: bool = False,
    ):
        super().__init__()
        self.causal = causal
        self.softmax_scale = softmax_scale
        self.drop = nn.Dropout(attention_dropout)
        self.dropout = attention_dropout
        self.softpick = softpick

    def forward(self, qkv, causal=None, key_padding_mask=None, bias=None):
        """
        Implements the multihead softmax attention.

        Args:
            qkv: The tensor containing the query, key, and value. (B, S, 3, H, D)
            causal: if passed, will override self.causal
            key_padding_mask: boolean mask to apply to the attention weights. True means to keep,
                False means to mask out. (B, S)
        """
        causal = self.causal if causal is None else causal
        q, k, v = qkv.unbind(dim=2)
        if not self.softpick:
            output = nn.functional.scaled_dot_product_attention(
                q,
                k,
                v,
                attn_mask=key_padding_mask,
                dropout_p=self.dropout,
                is_causal=causal,
            )
        else:
            softmax_scale = self.softmax_scale or 1.0 / math.sqrt(q.shape[-1])
            batch_size, seqlen = qkv.shape[0], qkv.shape[1]
            scores = torch.einsum("bthd,bshd->bhts", q, k * softmax_scale)
            if key_padding_mask is not None:
                padding_mask = torch.full(
                    (batch_size, seqlen),
                    -10000.0,
                    dtype=scores.dtype,
                    device=scores.device,
                )
                padding_mask.masked_fill_(key_padding_mask, 0.0)
                # TD [2022-09-30]: Adding is faster than masked_fill_ (idk why, just better kernel I guess)
                scores = scores + rearrange(padding_mask, "b s -> b 1 1 s")
            if causal:
                # "triu_tril_cuda_template" not implemented for 'BFloat16'
                # So we have to construct the mask in float
                causal_mask = torch.triu(
                    torch.full((seqlen, seqlen), -10000.0, device=scores.device), 1
                )
                # TD [2022-09-30]: Adding is faster than masked_fill_ (idk why, just better kernel I guess)
                scores = scores + causal_mask.to(dtype=scores.dtype)
            attention = (
                torch.softmax(scores, dim=-1, dtype=v.dtype)
                if not self.softpick
                else softpick(scores, dim=-1)
            )
            attention_drop = self.drop(attention)
            output = torch.einsum("bhts,bshd->bthd", attention_drop, v)
        return output


class CrossAttention(nn.Module):
    """Implement the scaled dot product attention with softmax.

    Args
        softmax_scale: The temperature to use for the softmax attention. Default to 1/sqrt(d_keys) where d_keys is computed at runtime
        attention_dropout: The dropout rate to apply to the attention. default to 0.0.
    """

    def __init__(self, causal=False, softmax_scale=None, attention_dropout=0.0):
        super().__init__()
        self.causal = causal
        self.softmax_scale = softmax_scale
        self.drop = nn.Dropout(attention_dropout)

    def forward(self, q, kv, causal=None, key_padding_mask=None, bias=None):
        """Implements the multihead softmax attention.

        Args
            q: The tensor containing the query. (B, Sq, H, D)
            kv: The tensor containing the key and value. (B, Sk, 2, H_k, D)
            causal: if passed, will override self.causal
            key_padding_mask: boolean mask to apply to the attention weights. True means to keep,
                False means to mask out. (B, Sk)
        """
        batch_size, seqlen_q = q.shape[0], q.shape[1]
        causal = self.causal if causal is None else causal
        seqlen_k = kv.shape[1]
        assert kv.shape[0] == batch_size and kv.shape[4] == q.shape[3]
        if kv.shape[3] != q.shape[2]:  # MQA/GQA
            kv = repeat(kv, "... hkv d -> ... (hkv g) d", g=q.shape[2] // kv.shape[3])
        k, v = kv.unbind(dim=2)
        softmax_scale = self.softmax_scale or 1.0 / math.sqrt(q.shape[-1])
        scores = torch.einsum("bthd,bshd->bhts", q, k * softmax_scale)
        if key_padding_mask is not None:
            padding_mask = torch.full(
                (batch_size, seqlen_k),
                -10000.0,
                dtype=scores.dtype,
                device=scores.device,
            )
            padding_mask.masked_fill_(key_padding_mask, 0.0)
            # TD [2022-09-30]: Adding is faster than masked_fill_ (idk why, just better kernel I guess)
            scores = scores + rearrange(padding_mask, "b s -> b 1 1 s")
        if causal:
            # causal mask needs to take into account the difference between seqlen_q and seqlen_k
            row_idx = rearrange(
                torch.arange(seqlen_q, device=q.device, dtype=torch.long), "s -> s 1"
            )
            col_idx = torch.arange(seqlen_k, device=kv.device, dtype=torch.long)
            sk = (
                seqlen_k
                if key_padding_mask is None
                else rearrange(key_padding_mask.sum(-1), "b -> b 1 1 1")
            )
            causal_mask = col_idx > row_idx + sk - seqlen_q
            scores = scores.masked_fill(causal_mask, -10000.0)
        attention = (
            torch.softmax(scores, dim=-1, dtype=v.dtype)
            if not self.softpick
            else softpick(scores, dim=-1)
        )
        attention_drop = self.drop(attention)
        output = torch.einsum("bhts,bshd->bthd", attention_drop, v)
        return output


class LinearResidual(nn.Linear):
    """Wrap nn.Linear to return the residual as well. For compatibility with FusedDense."""

    def forward(self, input: torch.Tensor) -> torch.Tensor:
        return super().forward(input), input


def _update_kv_cache(kv, inference_params, layer_idx):
    """kv: (batch_size, seqlen, 2, nheads, head_dim) or (batch_size, 1, 2, nheads, head_dim)"""
    # Pre-allocate memory for key-values for inference.
    num_heads, head_dim = kv.shape[-2:]
    if layer_idx not in inference_params.key_value_memory_dict:
        kv_cache = torch.empty(
            inference_params.max_batch_size,
            inference_params.max_seqlen,
            2,
            num_heads,
            head_dim,
            dtype=kv.dtype,
            device=kv.device,
        )
        inference_params.key_value_memory_dict[layer_idx] = kv_cache
    else:
        kv_cache = inference_params.key_value_memory_dict[layer_idx]
    # Adjust key and value for inference
    batch_start = inference_params.batch_size_offset
    batch_end = batch_start + kv.shape[0]
    sequence_start = inference_params.seqlen_offset
    sequence_end = sequence_start + kv.shape[1]
    assert batch_end <= kv_cache.shape[0]
    assert sequence_end <= kv_cache.shape[1]
    assert kv_cache is not None
    kv_cache[batch_start:batch_end, sequence_start:sequence_end, ...] = kv
    return kv_cache[batch_start:batch_end, :sequence_end, ...]


def softpick(x, dim=-1, eps=1e-6):
    # softpick function: relu(exp(x)-1) / sum(abs(exp(x)-1))
    # numerically stable version
    x_m = torch.max(x, dim=dim, keepdim=True).values
    x_m_e_m = torch.exp(-x_m)
    x_e_1 = torch.exp(x - x_m) - x_m_e_m
    r_x_e_1 = nn.functional.relu(x_e_1)
    a_x_e_1 = torch.where(x.isfinite(), torch.abs(x_e_1), 0)
    return r_x_e_1 / (
        torch.sum(a_x_e_1, dim=dim, keepdim=True) + eps
    )  # epsilon is only useful if all inputs are EXACTLY 0. we might not even need it


class MHA(nn.Module):
    def __init__(
        self,
        embed_dim: int,
        num_heads: int,
        num_heads_kv: int | None = None,
        cross_attn: bool = False,
        qkv_proj_bias: bool = True,
        out_proj_bias: bool = True,
        dropout: float = 0.0,
        softmax_scale: float | None = None,
        causal: bool = False,
        layer_idx: int | None = None,
        dwconv: bool = False,
        rotary_emb_dim: int = 0,
        rotary_emb_base: float = 10000.0,
        rotary_emb_scale_base: float | None = None,
        rotary_emb_interleaved: bool = False,
        use_alibi: bool = False,
        fused_bias_fc: bool = False,
        attn_type: str = "flash",
        return_residual: bool = False,
        checkpointing: bool = False,
        device: torch.device | None = None,
        dtype: torch.dtype | None = None,
        num_lsh_projections: int = 8,
        block_size: int = 128,
        sketcher_dim: int = 128,
        cross_dim: int = 128,
        softpick: bool = False,
    ) -> None:
        """
        MHA Multi-head self-attention and cross-attention

        Args:
            embed_dim
            num_heads_kv (int): can be used to toggle MQA / GQA. If None, use num_heads.
            return_residual (bool, optional): whether to return the input x along with the output. This is for
                performance reason: for post-norm architecture, returning the input allows us
                to fuse the backward of nn.Linear with the residual connection.
                Defaults to False.
            checkpointing (bool, optional): whether to use checkpointing to save memory.
                Defaults to False.
            num_heads_kv (int, optional): can be used to toggle MQA / GQA. If None, use num_heads.
            cross_attn (bool, optional): whether to use cross-attention. Defaults to False.
            qkv_proj_bias (bool, optional): whether to use bias in the query, key, value projection. Defaults to True.
            out_proj_bias (bool, optional): whether to use bias in the output projection. Defaults to True.
            dropout (float, optional): dropout rate. Defaults to 0.0.
            softmax_scale (float, optional): The temperature to use for the softmax attention.
            cross_dim (int, optional): dimension of the cross-attention element
            causal (bool, optional): whether to use causal attention. Defaults to False.
            layer_idx (int, optional): layer index for inference cache. Defaults to None.
            dwconv (bool, optional): whether to use depthwise convolution. Defaults to False.
            fused_bias_fc (bool, optional): whether to use fused_bias_fc. Defaults to False.
            attn_type (str, optional): whether to use FlashAttention. Defaults to "flash".
                - "flash": Use flash attention.
                - "normal": Use regular MHA attention.
                - "hyper": Use HyperAttention.
                - "criss-cross": Use Criss-Cross attention.
            device (torch.device, optional): device. Defaults to None.
            dtype (torch.dtype, optional): dtype. Defaults to None.
            num_lsh_projections (int, optional): number of LSH projections in HyperAttention. Defaults to 8.
            block_size (int, optional): block size for LSH in HyperAttention. Defaults to 128.
            sketcher_dim (int, optional): dimension of the sketcher. Defaults to 128.
        """
        factory_kwargs = {"device": device, "dtype": dtype}
        super().__init__()
        self.embed_dim = embed_dim
        self.cross_attn = cross_attn
        self.cross_dim = cross_dim
        self.causal = causal
        self.layer_idx = layer_idx
        self.dwconv = dwconv
        self.rotary_emb_dim = rotary_emb_dim
        self.attn_type = attn_type
        self.softpick = softpick
        if self.attn_type == "flash" and (flash_attn_kvpacked_func is None):
            print(
                "you requested flash transformer but it requires the flash package which is not installed"
            )
            print("falling back to regular transformer...")
            self.attn_type = "normal"

            # NOT flash transformer using the special tritton kernel
            # or parallelMHA (add the process group thing and faster)
        self.return_residual = return_residual
        self.checkpointing = checkpointing
        alibi_slopes = None

        self.num_heads = num_heads
        self.num_heads_kv = num_heads_kv if num_heads_kv is not None else num_heads
        assert (
            self.num_heads % self.num_heads_kv == 0
        ), "num_heads must be divisible by num_heads_kv"
        assert self.embed_dim % num_heads == 0, "embed_dim must be divisible by num_heads"
        self.head_dim = self.embed_dim // num_heads
        qkv_dim = self.head_dim * (self.num_heads + 2 * self.num_heads_kv)
        kv_dim = 2 * self.head_dim * self.num_heads_kv

        if self.rotary_emb_dim > 0:
            assert (
                not cross_attn
            ), "MHA with rotary embedding does not support cross-attention yet"
            assert RotaryEmbedding is not None, "rotary_emb is not installed"
            self.rotary_emb = RotaryEmbedding(
                self.rotary_emb_dim,
                base=rotary_emb_base,
                scale_base=rotary_emb_scale_base,
                interleaved=rotary_emb_interleaved,
                device=device,
            )

        if fused_bias_fc and FusedDense is None:
            raise ImportError("fused_dense is not installed")
        linear_cls = nn.Linear if not fused_bias_fc else FusedDense
        linear_resid_cls = (
            LinearResidual
            if not fused_bias_fc
            else partial(FusedDense, return_residual=True)
        )
        wqkv_cls = linear_cls if not self.return_residual else linear_resid_cls

        inner_attn_cls = partial(SelfAttention, softpick=self.softpick)
        if self.attn_type == "flash":
            inner_attn_cls = partial(
                FlashSelfAttention,
                alibi_slopes=alibi_slopes,
                softpick=self.softpick,
            )
        elif self.attn_type == "hyper":
            inner_attn_cls = partial(
                HyperSelfAttention,
                head_dim=self.head_dim,
                block_size=block_size,
                lsh_num_projs=num_lsh_projections,
            )
        inner_cross_attn_cls = partial(CrossAttention, softpick=self.softpick)
        if self.attn_type == "flash":
            inner_cross_attn_cls = partial(
                FlashCrossAttention,
                alibi_slopes=alibi_slopes,
                softpick=self.softpick,
            )
        elif self.attn_type == "hyper":
            inner_cross_attn_cls = partial(
                HyperCrossAttention,
                head_dim=self.head_dim,
                block_size=block_size,
                lsh_num_projs=num_lsh_projections,
            )

        if not self.cross_attn:
            self.Wqkv = wqkv_cls(embed_dim, qkv_dim, bias=qkv_proj_bias, **factory_kwargs)
        else:
            self.Wq = linear_cls(
                embed_dim, embed_dim, bias=qkv_proj_bias, **factory_kwargs
            )
            self.Wkv = wqkv_cls(cross_dim, kv_dim, bias=qkv_proj_bias, **factory_kwargs)
        if self.dwconv:
            if self.num_heads_kv == self.num_heads:
                self.dwconv_qkv = nn.Conv1d(
                    qkv_dim, qkv_dim, kernel_size=3, padding=2, groups=qkv_dim
                )
            else:
                self.dwconv_q = nn.Conv1d(
                    embed_dim, embed_dim, kernel_size=3, padding=2, groups=embed_dim
                )
                self.dwconv_kv = nn.Conv1d(
                    kv_dim, kv_dim, kernel_size=3, padding=2, groups=kv_dim
                )
        if self.attn_type == "criss-cross":
            self.Wqkv_criss_cross = wqkv_cls(sketcher_dim, qkv_dim, **factory_kwargs)
        self.inner_attn = inner_attn_cls(
            causal=causal,
            softmax_scale=softmax_scale,
            attention_dropout=dropout,
        )
        self.inner_cross_attn = inner_cross_attn_cls(
            causal=causal, softmax_scale=softmax_scale, attention_dropout=dropout
        )
        if self.attn_type == "criss-cross":
            self.inner_criss_cross_attn = inner_cross_attn_cls(
                causal=causal, softmax_scale=softmax_scale, attention_dropout=dropout
            )
            self.out_criss_cross = linear_cls(
                embed_dim,
                sketcher_dim,
                bias=out_proj_bias,
                **factory_kwargs,
            )
        self.out_proj = linear_cls(
            embed_dim, embed_dim, bias=out_proj_bias, **factory_kwargs
        )

    def allocate_inference_cache(self, batch_size, max_seqlen, dtype=None):
        dtype = self.out_proj.weight.dtype if dtype is None else dtype
        device = self.out_proj.weight.device
        return torch.empty(
            batch_size,
            max_seqlen,
            2,
            self.num_heads_kv,
            self.head_dim,
            dtype=dtype,
            device=device,
        )

    def _update_kv_cache(self, kv, inference_params):
        """kv: (batch_size, seqlen, 2, nheads, head_dim) or (batch_size, 1, 2, nheads, head_dim)"""
        assert not self.dwconv, "Generation does not support dwconv yet"
        assert (
            self.layer_idx is not None
        ), "Generation requires layer_idx in the constructor"
        return _update_kv_cache(kv, inference_params, self.layer_idx)

    def _apply_rotary_update_kvcache_attention(self, q, kv, inference_params):
        """
        Fast path that combine 3 steps: apply rotary to Q and K, update kv cache, and apply attention.
        q: (batch_size, seqlen_q, nheads, head_dim)
        kv: (batch_size, seqlen_k, 2, nheads_kv, head_dim)
        """
        assert inference_params is not None and inference_params.seqlen_offset > 0
        assert self.attn_type == "flash"
        if self.rotary_emb_dim > 0:
            assert self.rotary_emb.scale is None, "This code path does not support xPos"
            self.rotary_emb._update_cos_sin_cache(
                inference_params.max_seqlen, device=q.device, dtype=q.dtype
            )
            rotary_cos, rotary_sin = (
                self.rotary_emb._cos_cached,
                self.rotary_emb._sin_cached,
            )
        else:
            rotary_cos, rotary_sin = None, None
        batch = q.shape[0]
        kv_cache = inference_params.key_value_memory_dict[self.layer_idx][:batch]
        cache_seqlens = (
            inference_params.lengths_per_sample[:batch]
            if inference_params.lengths_per_sample is not None
            else inference_params.seqlen_offset
        )
        alibi_slopes = getattr(self.inner_cross_attn, "alibi_slopes", None)
        context = flash_attn_with_kvcache(
            q,
            kv_cache[:, :, 0],
            kv_cache[:, :, 1],
            kv[:, :, 0],
            kv[:, :, 1],
            rotary_cos=rotary_cos,
            rotary_sin=rotary_sin,
            cache_seqlens=cache_seqlens,
            softmax_scale=self.inner_cross_attn.softmax_scale,
            causal=self.inner_cross_attn.causal,
            rotary_interleaved=(
                self.rotary_emb.interleaved if self.rotary_emb_dim > 0 else False
            ),
            alibi_slopes=alibi_slopes,
        )
        return context

    def _update_kvcache_attention(self, q, kv, inference_params):
        """Write kv to inference_params, then do attention"""
        if (
            inference_params.seqlen_offset == 0
            or flash_attn_with_kvcache is None
            or not self.attn_type == "flash"
        ):
            # TODO: this only uses seqlen_offset and not lengths_per_sample.
            kv = self._update_kv_cache(kv, inference_params)
            return self.inner_cross_attn(q, kv)
        else:
            batch = q.shape[0]
            kv_cache = inference_params.key_value_memory_dict[self.layer_idx][:batch]
            cache_seqlens = (
                inference_params.lengths_per_sample[:batch]
                if inference_params.lengths_per_sample is not None
                else inference_params.seqlen_offset
            )
            alibi_slopes = getattr(self.inner_cross_attn, "alibi_slopes", None)
            return flash_attn_with_kvcache(
                q,
                kv_cache[:, :, 0],
                kv_cache[:, :, 1],
                kv[:, :, 0],
                kv[:, :, 1],
                cache_seqlens=cache_seqlens,
                softmax_scale=self.inner_cross_attn.softmax_scale,
                causal=self.inner_cross_attn.causal,
                alibi_slopes=alibi_slopes,
            )

    def forward(
        self,
        x: torch.Tensor,
        x_kv: torch.Tensor | None = None,
        key_padding_mask: torch.Tensor | None = None,
        cu_seqlens: torch.Tensor | None = None,
        max_seqlen: int | None = None,
        mixer_subset: torch.Tensor | None = None,
        inference_params: dict | None = None,
        return_qkv: bool = False,
        **kwargs,
    ):
        """
        Args:
            x: (batch, seqlen, hidden_dim) (where hidden_dim = num heads * head dim) if
                cu_seqlens is None and max_seqlen is None, else (total, hidden_dim) where total
                is the is the sum of the sequence lengths in the batch.
            x_kv: (batch, seqlen, hidden_dim), only applicable for cross-attention or criss-cross attention.If None, use x.
            cu_seqlens: (batch_size + 1,), dtype torch.int32. The cumulative sequence lengths
                of the sequences in the batch, used to index into x. Only applicable when using
                FlashAttention.
            max_seqlen: int. Maximum sequence length in the batch.
            key_padding_mask: boolean mask, True means to keep, False means to mask out.
                (batch, seqlen). Only applicable when not using FlashAttention.
            mixer_subset: for cross-attention only. If not None, will take a subset of x
                before applying the query projection. Useful for e.g., ViT where we only care
                about the CLS token in the last layer.
            inference_params: for generation. Adapted from Megatron-LM (and Apex)
            https://github.com/NVIDIA/apex/blob/3ff1a10f72ec07067c4e44759442329804ac5162/apex/transformer/testing/standalone_transformer_lm.py#L470
            return_qkv: whether to return the qkv tensor. Defaults to False.

        Returns
        -------
            out: (batch, seqlen, hidden_dim) if cu_seqlens is None and max_seqlen is None,
                else (total, hidden_dim) where total is the sum of the sequence lengths in the batch.
            qkv: (batch, seqlen, 3, hidden_dim) if cu_seqlens is None and max_seqlen is None,
                else (total, 3, hidden_dim) where total is the sum of the sequence lengths in the batch.
        """
        if cu_seqlens is not None:
            assert max_seqlen is not None
            assert key_padding_mask is None
            assert self.attn_type == "flash"
            assert not self.dwconv
            assert self.rotary_emb_dim == 0
        if key_padding_mask is not None:
            assert cu_seqlens is None
            assert max_seqlen is None
            assert not self.attn_type == "flash"
        if inference_params is not None:
            assert key_padding_mask is None
            assert cu_seqlens is None and max_seqlen is None
            assert not self.dwconv

        kwargs = (
            {}  # "cu_seqlens": cu_seqlens, "max_seqlen": max_seqlen, **kwargs}
            if self.attn_type != "normal"
            else {"key_padding_mask": key_padding_mask, **kwargs}
        )
        seqlen_offset = (
            0
            if inference_params is None
            else (
                inference_params.lengths_per_sample
                if inference_params.lengths_per_sample is not None
                else inference_params.seqlen_offset
            )
        )
        rotary_max_seqlen = (
            inference_params.max_seqlen if inference_params is not None else None
        )
        batch, seqlen = x.shape[:2]
        if (
            not self.cross_attn
            and self.num_heads_kv == self.num_heads
            and self.attn_type != "criss-cross"
        ):
            assert x_kv is None and mixer_subset is None
            if not self.return_residual:
                qkv = self.Wqkv(x)  # .to(torch.float16, device="cuda")
            else:
                qkv, x = self.Wqkv(x)
            if self.dwconv:
                qkv = rearrange(
                    self.dwconv_qkv(rearrange(qkv, "b s d -> b d s"))[..., :-2],
                    "b d s -> b s d",
                ).contiguous()
            qkv = rearrange(
                qkv, "... (three h d) -> ... three h d", three=3, d=self.head_dim
            )
            if (
                inference_params is None
                or inference_params.seqlen_offset == 0
                or (self.rotary_emb_dim == 0 or self.rotary_emb_dim % 16 != 0)
                or not self.attn_type == "flash"
            ):
                if self.rotary_emb_dim > 0:
                    qkv = self.rotary_emb(
                        qkv, seqlen_offset=seqlen_offset, max_seqlen=rotary_max_seqlen
                    )
                if inference_params is None:
                    if not self.checkpointing:
                        context = self.inner_attn(qkv, **kwargs)
                    else:
                        context = torch.utils.checkpoint.checkpoint(
                            self.inner_attn, qkv, **kwargs
                        )
                else:
                    context = self._update_kvcache_attention(
                        qkv[:, :, 0], qkv[:, :, 1:], inference_params
                    )
            else:
                context = self._apply_rotary_update_kvcache_attention(
                    qkv[:, :, 0], qkv[:, :, 1:], inference_params
                )
        else:
            if self.cross_attn:
                if not self.return_residual:
                    q = self.Wq(x if mixer_subset is None else x[:, mixer_subset])
                    kv = self.Wkv(x_kv if x_kv is not None else x)
                else:
                    if x_kv is not None:
                        kv, x_kv = self.Wkv(x_kv)
                    else:
                        kv, x = self.Wkv(x)
                    q = self.Wq(x if mixer_subset is None else x[:, mixer_subset])
            else:
                if not self.return_residual:
                    qkv = self.Wqkv(x)
                else:
                    qkv, x = self.Wqkv(x)
                q = qkv[..., : self.num_heads * self.head_dim]
                kv = qkv[..., self.num_heads * self.head_dim :]
                if self.attn_type == "criss-cross":
                    cc_qkv = self.Wqkv_criss_cross(x_kv)
                    cc_q = cc_qkv[..., : self.num_heads * self.head_dim]
                    cc_kv = cc_qkv[..., self.num_heads * self.head_dim :]
                    cc_q = rearrange(cc_q, "... (h d) -> ... h d", d=self.head_dim)
                    cc_kv = rearrange(
                        cc_kv,
                        "... (two hkv d) -> ... two hkv d",
                        two=2,
                        d=self.head_dim,
                    )
            q = rearrange(q, "... (h d) -> ... h d", d=self.head_dim)
            kv = rearrange(kv, "... (two hkv d) -> ... two hkv d", two=2, d=self.head_dim)
            # TODO: to change for criss-cross

            if self.dwconv:
                q = rearrange(
                    self.dwconv_q(rearrange(q, "b s d -> b d s"))[..., :-2],
                    "b d s -> b s d",
                ).contiguous()
                kv = rearrange(
                    self.dwconv_kv(rearrange(kv, "b s d -> b d s"))[..., :-2],
                    "b d s -> b s d",
                ).contiguous()
                if self.attn_type == "criss-cross":
                    cc_q = rearrange(
                        self.dwconv_q(rearrange(cc_q, "b s d -> b d s"))[..., :-2],
                        "b d s -> b s d",
                    ).contiguous()
                    cc_kv = rearrange(
                        self.dwconv_kv(rearrange(cc_kv, "b s d -> b d s"))[..., :-2],
                        "b d s -> b s d",
                    ).contiguous()
            if (
                inference_params is None
                or inference_params.seqlen_offset == 0
                or (self.rotary_emb_dim == 0 or self.rotary_emb_dim % 16 != 0)
                or not self.attn_type == "flash"
            ):
                if self.rotary_emb_dim > 0:
                    q, kv = self.rotary_emb(
                        q, kv, seqlen_offset=seqlen_offset, max_seqlen=rotary_max_seqlen
                    )
                if inference_params is None:
                    if not self.checkpointing:
                        if self.attn_type == "criss-cross":
                            cc_context = self.inner_criss_cross_attn(cc_q, kv, **kwargs)
                        context = self.inner_cross_attn(
                            q,
                            kv if self.attn_type != "criss-cross" else cc_kv,
                            **kwargs,
                        )
                    else:
                        if self.attn_type == "criss-cross":
                            cc_context = self.inner_criss_cross_attn(cc_q, kv, **kwargs)
                        context = torch.utils.checkpoint.checkpoint(
                            self.inner_cross_attn,
                            q,
                            kv if self.attn_type != "criss-cross" else cc_kv,
                            **kwargs,
                        )
                else:
                    context = self._update_kvcache_attention(q, kv, inference_params)
            else:
                context = self._apply_rotary_update_kvcache_attention(
                    q, kv, inference_params
                )
            if return_qkv:
                qkv = torch.cat(
                    [
                        q.unsqueeze(2),
                        kv.repeat_interleave(self.num_heads // self.num_heads_kv, dim=3),
                    ],
                    dim=2,
                )
                #    [
                #        torch.cat([q, cc_q], dim=1).unsqueeze(2),
                #        torch.cat([kv, cc_kv], dim=1).repeat_interleave(
                #            self.num_heads // self.num_heads_kv, dim=3
                #        ),
                #    ],
                #    dim=2,
                # )
        out = self.out_proj(rearrange(context, "... h d -> ... (h d)"))
        if self.attn_type == "criss-cross":
            out = (
                out,
                self.out_criss_cross(rearrange(cc_context, "... h d -> ... (h d)")),
            )
        if return_qkv:
            return out if not self.return_residual else (out, x), qkv
        else:
            return out if not self.return_residual else (out, x)
