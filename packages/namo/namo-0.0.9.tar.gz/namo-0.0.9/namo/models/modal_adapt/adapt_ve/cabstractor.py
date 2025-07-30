from functools import partial
from torch import nn
import torch.nn.functional as F
from transformers.activations import ACT2FN
import math
from torch.nn import LayerNorm
import torch
from timm.models.regnet import RegStage
from timm.layers import LayerNorm, LayerNorm2d


class GLU(nn.Module):
    def __init__(self, hidden_size, ffn_hidden_size, in_features):
        super().__init__()
        self.linear_proj = nn.Linear(in_features, hidden_size, bias=False)
        self.norm1 = nn.LayerNorm(hidden_size)
        self.act1 = nn.GELU()
        self.act2 = nn.functional.silu
        self.dense_h_to_4h = nn.Linear(hidden_size, ffn_hidden_size, bias=False)
        self.gate_proj = nn.Linear(hidden_size, ffn_hidden_size, bias=False)
        self.dense_4h_to_h = nn.Linear(ffn_hidden_size, hidden_size, bias=False)

    def forward(self, x):
        x = self.linear_proj(x)
        x = self.act1(self.norm1(x))
        x = self.act2(self.gate_proj(x)) * self.dense_h_to_4h(x)
        x = self.dense_4h_to_h(x)
        return x


class MlpGLU(nn.Module):
    def __init__(self, in_hidden_size, out_hidden_size):
        super(MlpGLU, self).__init__()

        ffn_hidden_size = (
            out_hidden_size * 4
        )  # out_hidden_size * 4 3584 * 4 = 14336 5120x4=20480 12B
        self.linear_proj = GLU(
            hidden_size=out_hidden_size,
            ffn_hidden_size=ffn_hidden_size,
            in_features=in_hidden_size,
        )

    def forward(self, x, attention_mask: torch.Tensor = None):
        x = self.linear_proj(x)
        return x


class CAbstractor(nn.Module):

    def __init__(self, in_hidden_size, out_hidden_size, down_rate=4):
        super(CAbstractor, self).__init__()
        # ffn_hidden_size = 13696
        ffn_hidden_size = out_hidden_size * 4  # out_hidden_size * 4 3584 * 4 = 14336
        self.linear_proj = GLU(
            hidden_size=out_hidden_size,
            ffn_hidden_size=ffn_hidden_size,
            in_features=in_hidden_size,
        )
        self.down_rate = down_rate
        if self.down_rate == 4:
            # 考虑对d4进行简化，我们能不用两个卷积就不用两个卷积
            # 考虑直接用线性插值到 11x11 = 112，这样不管输入多大，都是112，再把输入加大
            conv = nn.Conv2d(
                in_channels=in_hidden_size,
                out_channels=in_hidden_size,
                kernel_size=2,
                stride=2,
            )
            conv2 = nn.Conv2d(
                in_channels=in_hidden_size,
                out_channels=in_hidden_size,
                kernel_size=2,
                stride=2,
            )
            self.conv = nn.Sequential(*[conv, conv2])
        elif self.down_rate == 8:
            # downsample 4x, 千万不能下采样两次
            conv = nn.Conv2d(
                in_channels=in_hidden_size,
                out_channels=in_hidden_size,
                kernel_size=2,
                stride=2,
            )
            conv2 = nn.Conv2d(
                in_channels=in_hidden_size,
                out_channels=in_hidden_size,
                kernel_size=2,
                stride=2,
            )
            # pool = nn.AdaptiveAvgPool2d((8, 8))
            # 用interpolate, don't using Pool
            pool = nn.AdaptiveAvgPool2d((4, 4))
            self.conv = nn.Sequential(*[conv, conv2, pool])
        elif self.down_rate == 7:
            conv = nn.Conv2d(
                in_channels=in_hidden_size,
                out_channels=in_hidden_size,
                kernel_size=2,
                stride=2,
            )
            pool = nn.AdaptiveAvgPool2d((7, 7))
            self.conv = nn.Sequential(*[conv, pool])
        elif self.down_rate == 2:
            self.conv = nn.Conv2d(
                in_channels=in_hidden_size,
                out_channels=in_hidden_size,
                kernel_size=2,
                stride=2,
            )
        else:
            print(f"unsupported downsample rate for now!")
        self.scaling_factor = 8

        # RegBlock = partial(
        #     RegStage,
        #     stride=1,
        #     dilation=1,
        #     act_layer=nn.SiLU,
        #     norm_layer=LayerNorm2d,
        # )

    def forward(self, x, attention_mask: torch.Tensor = None):
        b, s, h = x.shape
        grid_size = int(s**0.5)
        x = x.view(b, grid_size, grid_size, h).permute(0, 3, 1, 2)
        x = self.conv(x)

        x = x.flatten(2).transpose(1, 2)
        # print(f'x: {x.shape}')
        x = self.linear_proj(x)
        # x = x / self.scaling_factor
        # print(f'x: {x.shape}')
        # 504, d4 -> 81 tokens/img 16x
        return x
