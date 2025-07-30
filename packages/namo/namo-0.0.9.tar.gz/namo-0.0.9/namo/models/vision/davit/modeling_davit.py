# coding=utf-8
# Copyright 2024 Microsoft and the HuggingFace Inc. team. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""PyTorch Florence-2 model."""
from dataclasses import dataclass
from typing import List, Optional, Tuple, Union

import math
import torch
import torch.utils.checkpoint
from torch import nn
import torch.nn.functional as F
import torch.utils.checkpoint as checkpoint
from torch.nn import CrossEntropyLoss
from collections import OrderedDict
from einops import rearrange
from timm.models.layers import DropPath, trunc_normal_

from transformers.modeling_utils import PreTrainedModel
from transformers.utils import (
    ModelOutput,
    add_start_docstrings,
    add_start_docstrings_to_model_forward,
    is_flash_attn_2_available,
    logging,
    replace_return_docstrings,
    is_flash_attn_2_available,
    is_flash_attn_greater_or_equal_2_10,
)
from .configuration_florence2 import Florence2Config
from .configuration_florence2 import Florence2LanguageConfig
from .configuration_florence2 import Florence2VisionConfig


from transformers.activations import ACT2FN
from transformers.modeling_attn_mask_utils import (
    _prepare_4d_attention_mask,
    _prepare_4d_attention_mask_for_sdpa,
    _prepare_4d_causal_attention_mask,
    _prepare_4d_causal_attention_mask_for_sdpa,
)
from transformers.modeling_outputs import (
    BaseModelOutput,
    BaseModelOutputWithPastAndCrossAttentions,
    Seq2SeqLMOutput,
    Seq2SeqModelOutput,
)


if is_flash_attn_2_available():
    from flash_attn.bert_padding import index_first_axis, pad_input, unpad_input  # noqa

logger = logging.get_logger(__name__)

_CONFIG_FOR_DOC = "Florence2Config"


class LearnedAbsolutePositionEmbedding2D(nn.Module):
    """
    This module learns positional embeddings up to a fixed maximum size.
    """

    def __init__(self, embedding_dim=256, num_pos=50):
        super().__init__()
        self.row_embeddings = nn.Embedding(num_pos, embedding_dim // 2)
        self.column_embeddings = nn.Embedding(
            num_pos, embedding_dim - (embedding_dim // 2)
        )

    def forward(self, pixel_values):
        """
        pixel_values: (batch_size, height, width, num_channels)
        returns: (batch_size, height, width, embedding_dim * 2)
        """
        if len(pixel_values.shape) != 4:
            raise ValueError("pixel_values must be a 4D tensor")
        height, width = pixel_values.shape[1:3]
        width_values = torch.arange(width, device=pixel_values.device)
        height_values = torch.arange(height, device=pixel_values.device)
        x_emb = self.column_embeddings(width_values)
        y_emb = self.row_embeddings(height_values)
        # (height, width, embedding_dim * 2)
        pos = torch.cat(
            [
                x_emb.unsqueeze(0).repeat(height, 1, 1),
                y_emb.unsqueeze(1).repeat(1, width, 1),
            ],
            dim=-1,
        )
        # (embedding_dim * 2, height, width)
        pos = pos.permute(2, 0, 1)
        pos = pos.unsqueeze(0)
        # (batch_size, embedding_dim * 2, height, width)
        pos = pos.repeat(pixel_values.shape[0], 1, 1, 1)
        # (batch_size, height, width, embedding_dim * 2)
        pos = pos.permute(0, 2, 3, 1)
        return pos


class PositionalEmbeddingCosine1D(nn.Module):
    """
    This class implements a very simple positional encoding. It follows closely
    the encoder from the link below:
    https://pytorch.org/tutorials/beginner/translation_transformer.html

    Args:
        embed_dim: The dimension of the embeddings.
        dropout_prob: The dropout probability.
        max_seq_len: The maximum length to precompute the positional encodings.
    """

    def __init__(self, embed_dim: int = 512, max_seq_len: int = 1024) -> None:
        super(PositionalEmbeddingCosine1D, self).__init__()
        self.embed_dim = embed_dim
        self.max_seq_len = max_seq_len
        # Generate the sinusoidal arrays.
        factor = math.log(10000)
        denominator = torch.exp(
            -factor * torch.arange(0, self.embed_dim, 2) / self.embed_dim
        )
        # Matrix where rows correspond to a positional embedding as a function
        # of the position index (i.e., the row index).
        frequencies = (
            torch.arange(0, self.max_seq_len).reshape(self.max_seq_len, 1) * denominator
        )
        pos_idx_to_embed = torch.zeros((self.max_seq_len, self.embed_dim))
        # Populate uneven entries.
        pos_idx_to_embed[:, 0::2] = torch.sin(frequencies)
        pos_idx_to_embed[:, 1::2] = torch.cos(frequencies)
        # Save the positional embeddings in a constant buffer.
        self.register_buffer("pos_idx_to_embed", pos_idx_to_embed)

    def forward(self, seq_embeds: torch.Tensor) -> torch.Tensor:
        """
        Args:
            seq_embeds: The sequence embeddings in order. Allowed size:
                1. [T, D], where T is the length of the sequence, and D is the
                frame embedding dimension.
                2. [B, T, D], where B is the batch size and T and D are the
                same as above.

        Returns a tensor of with the same dimensions as the input: i.e.,
        [1, T, D] or [T, D].
        """
        shape_len = len(seq_embeds.shape)
        assert 2 <= shape_len <= 3
        len_seq = seq_embeds.size(-2)
        assert len_seq <= self.max_seq_len
        pos_embeds = self.pos_idx_to_embed[0 : seq_embeds.size(-2), :]
        # Adapt pre-computed positional embeddings to the input.
        if shape_len == 3:
            pos_embeds = pos_embeds.view((1, pos_embeds.size(0), pos_embeds.size(1)))
        return pos_embeds


class LearnedAbsolutePositionEmbedding1D(nn.Module):
    """
    Learnable absolute positional embeddings for 1D sequences.

    Args:
        embed_dim: The dimension of the embeddings.
        max_seq_len: The maximum length to precompute the positional encodings.
    """

    def __init__(self, embedding_dim: int = 512, num_pos: int = 1024) -> None:
        super(LearnedAbsolutePositionEmbedding1D, self).__init__()
        self.embeddings = nn.Embedding(num_pos, embedding_dim)
        self.num_pos = num_pos

    def forward(self, seq_embeds: torch.Tensor) -> torch.Tensor:
        """
        Args:
            seq_embeds: The sequence embeddings in order. Allowed size:
                1. [T, D], where T is the length of the sequence, and D is the
                frame embedding dimension.
                2. [B, T, D], where B is the batch size and T and D are the
                same as above.

        Returns a tensor of with the same dimensions as the input: i.e.,
        [1, T, D] or [T, D].
        """
        shape_len = len(seq_embeds.shape)
        assert 2 <= shape_len <= 3
        len_seq = seq_embeds.size(-2)
        assert len_seq <= self.num_pos
        # [T, D]
        pos_embeds = self.embeddings(torch.arange(len_seq).to(seq_embeds.device))
        # Adapt pre-computed positional embeddings to the input.
        if shape_len == 3:
            pos_embeds = pos_embeds.view((1, pos_embeds.size(0), pos_embeds.size(1)))
        return pos_embeds


class MySequential(nn.Sequential):
    def forward(self, *inputs):
        for module in self._modules.values():
            if type(inputs) == tuple:
                inputs = module(*inputs)
            else:
                inputs = module(inputs)
        return inputs


class PreNorm(nn.Module):
    def __init__(self, norm, fn, drop_path=None):
        super().__init__()
        self.norm = norm
        self.fn = fn
        self.drop_path = drop_path

    def forward(self, x, *args, **kwargs):
        shortcut = x
        if self.norm != None:
            x, size = self.fn(self.norm(x), *args, **kwargs)
        else:
            x, size = self.fn(x, *args, **kwargs)

        if self.drop_path:
            x = self.drop_path(x)

        x = shortcut + x

        return x, size


class Mlp(nn.Module):
    def __init__(
        self,
        in_features,
        hidden_features=None,
        out_features=None,
        act_layer=nn.GELU,
    ):
        super().__init__()
        out_features = out_features or in_features
        hidden_features = hidden_features or in_features
        self.net = nn.Sequential(
            OrderedDict(
                [
                    ("fc1", nn.Linear(in_features, hidden_features)),
                    ("act", act_layer()),
                    ("fc2", nn.Linear(hidden_features, out_features)),
                ]
            )
        )

    def forward(self, x, size):
        return self.net(x), size


class DepthWiseConv2d(nn.Module):
    def __init__(
        self,
        dim_in,
        kernel_size,
        padding,
        stride,
        bias=True,
    ):
        super().__init__()
        self.dw = nn.Conv2d(
            dim_in,
            dim_in,
            kernel_size=kernel_size,
            padding=padding,
            groups=dim_in,
            stride=stride,
            bias=bias,
        )

    def forward(self, x, size):
        B, N, C = x.shape
        H, W = size
        assert N == H * W

        x = self.dw(x.transpose(1, 2).view(B, C, H, W))
        size = (x.size(-2), x.size(-1))
        x = x.flatten(2).transpose(1, 2)
        return x, size


class ConvEmbed(nn.Module):
    """Image to Patch Embedding"""

    def __init__(
        self,
        patch_size=7,
        in_chans=3,
        embed_dim=64,
        stride=4,
        padding=2,
        norm_layer=None,
        pre_norm=True,
    ):
        super().__init__()
        self.patch_size = patch_size

        self.proj = nn.Conv2d(
            in_chans, embed_dim, kernel_size=patch_size, stride=stride, padding=padding
        )

        dim_norm = in_chans if pre_norm else embed_dim
        self.norm = norm_layer(dim_norm) if norm_layer else None

        self.pre_norm = pre_norm

    def forward(self, x, size):
        H, W = size
        if len(x.size()) == 3:
            if self.norm and self.pre_norm:
                x = self.norm(x)
            x = rearrange(x, "b (h w) c -> b c h w", h=H, w=W)

        x = self.proj(x)

        _, _, H, W = x.shape
        x = rearrange(x, "b c h w -> b (h w) c")
        if self.norm and not self.pre_norm:
            x = self.norm(x)

        return x, (H, W)


class ChannelAttention(nn.Module):
    def __init__(self, dim, groups=8, qkv_bias=True):
        super().__init__()

        self.groups = groups
        self.qkv = nn.Linear(dim, dim * 3, bias=qkv_bias)
        self.proj = nn.Linear(dim, dim)

    def forward(self, x, size):
        B, N, C = x.shape

        qkv = (
            self.qkv(x)
            .reshape(B, N, 3, self.groups, C // self.groups)
            .permute(2, 0, 3, 1, 4)
        )
        q, k, v = qkv[0], qkv[1], qkv[2]

        q = q * (float(N) ** -0.5)
        attention = q.transpose(-1, -2) @ k
        attention = attention.softmax(dim=-1)
        x = (attention @ v.transpose(-1, -2)).transpose(-1, -2)
        x = x.transpose(1, 2).reshape(B, N, C)
        x = self.proj(x)
        return x, size


class ChannelBlock(nn.Module):
    def __init__(
        self,
        dim,
        groups,
        mlp_ratio=4.0,
        qkv_bias=True,
        drop_path_rate=0.0,
        act_layer=nn.GELU,
        norm_layer=nn.LayerNorm,
        conv_at_attn=True,
        conv_at_ffn=True,
    ):
        super().__init__()

        drop_path = DropPath(drop_path_rate) if drop_path_rate > 0.0 else nn.Identity()

        self.conv1 = (
            PreNorm(None, DepthWiseConv2d(dim, 3, 1, 1)) if conv_at_attn else None
        )
        self.channel_attn = PreNorm(
            norm_layer(dim),
            ChannelAttention(dim, groups=groups, qkv_bias=qkv_bias),
            drop_path,
        )
        self.conv2 = (
            PreNorm(None, DepthWiseConv2d(dim, 3, 1, 1)) if conv_at_ffn else None
        )
        self.ffn = PreNorm(
            norm_layer(dim),
            Mlp(
                in_features=dim,
                hidden_features=int(dim * mlp_ratio),
                act_layer=act_layer,
            ),
            drop_path,
        )

    def forward(self, x, size):
        if self.conv1:
            x, size = self.conv1(x, size)
        x, size = self.channel_attn(x, size)

        if self.conv2:
            x, size = self.conv2(x, size)
        x, size = self.ffn(x, size)

        return x, size


def window_partition(x, window_size: int):
    B, H, W, C = x.shape
    x = x.view(B, H // window_size, window_size, W // window_size, window_size, C)
    windows = (
        x.permute(0, 1, 3, 2, 4, 5).contiguous().view(-1, window_size, window_size, C)
    )
    return windows


def window_reverse(windows, batch_size: int, window_size: int, H: int, W: int):
    B = batch_size
    # this will cause onnx conversion failed for dynamic axis, because treated as constant
    # int(windows.shape[0] / (H * W / window_size / window_size))
    x = windows.view(
        B, H // window_size, W // window_size, window_size, window_size, -1
    )
    x = x.permute(0, 1, 3, 2, 4, 5).contiguous().view(B, H, W, -1)
    return x


class WindowAttention(nn.Module):
    def __init__(self, dim, num_heads, window_size, qkv_bias=True):

        super().__init__()
        self.dim = dim
        self.window_size = window_size
        self.num_heads = num_heads
        head_dim = dim // num_heads
        self.scale = float(head_dim) ** -0.5

        self.qkv = nn.Linear(dim, dim * 3, bias=qkv_bias)
        self.proj = nn.Linear(dim, dim)

        self.softmax = nn.Softmax(dim=-1)

    def forward(self, x, size):

        H, W = size
        B, L, C = x.shape
        assert L == H * W, "input feature has wrong size"

        x = x.view(B, H, W, C)

        pad_l = pad_t = 0
        pad_r = (self.window_size - W % self.window_size) % self.window_size
        pad_b = (self.window_size - H % self.window_size) % self.window_size
        x = F.pad(x, (0, 0, pad_l, pad_r, pad_t, pad_b))
        _, Hp, Wp, _ = x.shape

        x = window_partition(x, self.window_size)
        x = x.view(-1, self.window_size * self.window_size, C)

        # W-MSA/SW-MSA
        # attn_windows = self.attn(x_windows)

        B_, N, C = x.shape
        qkv = (
            self.qkv(x)
            .reshape(B_, N, 3, self.num_heads, C // self.num_heads)
            .permute(2, 0, 3, 1, 4)
        )
        q, k, v = qkv[0], qkv[1], qkv[2]

        q = q * self.scale
        attn = q @ k.transpose(-2, -1)
        attn = self.softmax(attn)

        x = (attn @ v).transpose(1, 2).reshape(B_, N, C)
        x = self.proj(x)

        # merge windows
        x = x.view(-1, self.window_size, self.window_size, C)
        x = window_reverse(x, B, self.window_size, Hp, Wp)

        if pad_r > 0 or pad_b > 0:
            x = x[:, :H, :W, :].contiguous()

        x = x.view(B, H * W, C)

        return x, size


class SpatialBlock(nn.Module):
    def __init__(
        self,
        dim,
        num_heads,
        window_size,
        mlp_ratio=4.0,
        qkv_bias=True,
        drop_path_rate=0.0,
        act_layer=nn.GELU,
        norm_layer=nn.LayerNorm,
        conv_at_attn=True,
        conv_at_ffn=True,
    ):
        super().__init__()

        drop_path = DropPath(drop_path_rate) if drop_path_rate > 0.0 else nn.Identity()

        self.conv1 = (
            PreNorm(None, DepthWiseConv2d(dim, 3, 1, 1)) if conv_at_attn else None
        )
        self.window_attn = PreNorm(
            norm_layer(dim),
            WindowAttention(dim, num_heads, window_size, qkv_bias=qkv_bias),
            drop_path,
        )
        self.conv2 = (
            PreNorm(None, DepthWiseConv2d(dim, 3, 1, 1)) if conv_at_ffn else None
        )
        self.ffn = PreNorm(
            norm_layer(dim),
            Mlp(
                in_features=dim,
                hidden_features=int(dim * mlp_ratio),
                act_layer=act_layer,
            ),
            drop_path,
        )

    def forward(self, x, size):
        if self.conv1:
            x, size = self.conv1(x, size)
        x, size = self.window_attn(x, size)

        if self.conv2:
            x, size = self.conv2(x, size)
        x, size = self.ffn(x, size)
        return x, size


class DaViT(nn.Module):
    """DaViT: Dual-Attention Transformer

    Args:
        in_chans (int): Number of input image channels. Default: 3.
        num_classes (int): Number of classes for classification head. Default: 1000.
        patch_size (tuple(int)): Patch size of convolution in different stages. Default: (7, 2, 2, 2).
        patch_stride (tuple(int)): Patch stride of convolution in different stages. Default: (4, 2, 2, 2).
        patch_padding (tuple(int)): Patch padding of convolution in different stages. Default: (3, 0, 0, 0).
        patch_prenorm (tuple(bool)): If True, perform norm before convlution layer. Default: (True, False, False, False).
        embed_dims (tuple(int)): Patch embedding dimension in different stages. Default: (64, 128, 192, 256).
        num_heads (tuple(int)): Number of spatial attention heads in different stages. Default: (4, 8, 12, 16).
        num_groups (tuple(int)): Number of channel groups in different stages. Default: (4, 8, 12, 16).
        window_size (int): Window size. Default: 7.
        mlp_ratio (float): Ratio of mlp hidden dim to embedding dim. Default: 4.
        qkv_bias (bool): If True, add a learnable bias to query, key, value. Default: True.
        drop_path_rate (float): Stochastic depth rate. Default: 0.1.
        norm_layer (nn.Module): Normalization layer. Default: nn.LayerNorm.
        enable_checkpoint (bool): If True, enable checkpointing. Default: False.
        conv_at_attn (bool): If True, performe depthwise convolution before attention layer. Default: True.
        conv_at_ffn (bool): If True, performe depthwise convolution before ffn layer. Default: True.
    """

    def __init__(
        self,
        in_chans=3,
        num_classes=1000,
        depths=(1, 1, 3, 1),
        patch_size=(7, 2, 2, 2),
        patch_stride=(4, 2, 2, 2),
        patch_padding=(3, 0, 0, 0),
        patch_prenorm=(False, False, False, False),
        embed_dims=(64, 128, 192, 256),
        num_heads=(3, 6, 12, 24),
        num_groups=(3, 6, 12, 24),
        window_size=7,
        mlp_ratio=4.0,
        qkv_bias=True,
        drop_path_rate=0.1,
        norm_layer=nn.LayerNorm,
        enable_checkpoint=False,
        conv_at_attn=True,
        conv_at_ffn=True,
    ):
        super().__init__()

        self.num_classes = num_classes
        self.embed_dims = embed_dims
        self.num_heads = num_heads
        self.num_groups = num_groups
        self.num_stages = len(self.embed_dims)
        self.enable_checkpoint = enable_checkpoint
        assert self.num_stages == len(self.num_heads) == len(self.num_groups)

        num_stages = len(embed_dims)
        dpr = [x.item() for x in torch.linspace(0, drop_path_rate, sum(depths) * 2)]

        depth_offset = 0
        convs = []
        blocks = []
        for i in range(num_stages):
            conv_embed = ConvEmbed(
                patch_size=patch_size[i],
                stride=patch_stride[i],
                padding=patch_padding[i],
                in_chans=in_chans if i == 0 else self.embed_dims[i - 1],
                embed_dim=self.embed_dims[i],
                norm_layer=norm_layer,
                pre_norm=patch_prenorm[i],
            )
            convs.append(conv_embed)

            block = MySequential(
                *[
                    MySequential(
                        OrderedDict(
                            [
                                (
                                    "spatial_block",
                                    SpatialBlock(
                                        embed_dims[i],
                                        num_heads[i],
                                        window_size,
                                        drop_path_rate=dpr[depth_offset + j * 2],
                                        qkv_bias=qkv_bias,
                                        mlp_ratio=mlp_ratio,
                                        conv_at_attn=conv_at_attn,
                                        conv_at_ffn=conv_at_ffn,
                                    ),
                                ),
                                (
                                    "channel_block",
                                    ChannelBlock(
                                        embed_dims[i],
                                        num_groups[i],
                                        drop_path_rate=dpr[depth_offset + j * 2 + 1],
                                        qkv_bias=qkv_bias,
                                        mlp_ratio=mlp_ratio,
                                        conv_at_attn=conv_at_attn,
                                        conv_at_ffn=conv_at_ffn,
                                    ),
                                ),
                            ]
                        )
                    )
                    for j in range(depths[i])
                ]
            )
            blocks.append(block)
            depth_offset += depths[i] * 2

        self.convs = nn.ModuleList(convs)
        self.blocks = nn.ModuleList(blocks)

        self.norms = norm_layer(self.embed_dims[-1])
        self.avgpool = nn.AdaptiveAvgPool1d(1)
        self.head = (
            nn.Linear(self.embed_dims[-1], num_classes)
            if num_classes > 0
            else nn.Identity()
        )

        self.apply(self._init_weights)

    @property
    def dim_out(self):
        return self.embed_dims[-1]

    def _init_weights(self, m):
        if isinstance(m, nn.Linear):
            trunc_normal_(m.weight, std=0.02)
            if m.bias is not None:
                nn.init.constant_(m.bias, 0)
        elif isinstance(m, nn.Conv2d):
            nn.init.normal_(m.weight, std=0.02)
            for name, _ in m.named_parameters():
                if name in ["bias"]:
                    nn.init.constant_(m.bias, 0)
        elif isinstance(m, nn.LayerNorm):
            nn.init.constant_(m.weight, 1.0)
            nn.init.constant_(m.bias, 0)
        elif isinstance(m, nn.BatchNorm2d):
            nn.init.constant_(m.weight, 1.0)
            nn.init.constant_(m.bias, 0)

    def forward_features_unpool(self, x):
        """
        forward until avg pooling
        Args:
            x (_type_): input image tensor
        """
        input_size = (x.size(2), x.size(3))
        for conv, block in zip(self.convs, self.blocks):
            x, input_size = conv(x, input_size)
            if self.enable_checkpoint:
                x, input_size = checkpoint.checkpoint(block, x, input_size)
            else:
                x, input_size = block(x, input_size)
        return x

    def forward_features(self, x):
        x = self.forward_features_unpool(x)

        # (batch_size, num_tokens, token_dim)
        x = self.avgpool(x.transpose(1, 2))
        # (batch_size, 1, num_tokens)
        x = torch.flatten(x, 1)
        x = self.norms(x)

        return x

    def forward(self, x):
        x = self.forward_features(x)
        x = self.head(x)
        return x

    @classmethod
    def from_config(cls, config):
        return cls(
            depths=config.depths,
            embed_dims=config.dim_embed,
            num_heads=config.num_heads,
            num_groups=config.num_groups,
            patch_size=config.patch_size,
            patch_stride=config.patch_stride,
            patch_padding=config.patch_padding,
            patch_prenorm=config.patch_prenorm,
            drop_path_rate=config.drop_path_rate,
            window_size=config.window_size,
        )


if is_flash_attn_2_available():
    from flash_attn import flash_attn_func, flash_attn_varlen_func
    from flash_attn.bert_padding import index_first_axis, pad_input, unpad_input  # noqa
