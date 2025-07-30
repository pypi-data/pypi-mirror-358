from functools import partial
import re
from torch import nn
import torch
import torch.nn.functional as F
from transformers.activations import ACT2FN
from .components import GLU
from namo.utils.utils import rank0_print


class PixelShuffleLayer(nn.Module):
    def __init(self):
        super(PixelShuffleLayer, self).__init__()

    def forward(self, x, scale_factor=0.5):
        if len(x.shape) == 3:
            # 2d version of pixelshuffle?
            # B, L, H [3, 2304, 768]
            # how to downsample the token Length to a smaller value?
            # the 2304 has padding, shall we remove the padding?
            pass
        else:
            n, w, h, c = x.size()

            # handle if w h not even
            pad_w = 0
            pad_h = 0
            if w % int(1 / scale_factor) != 0:
                pad_w = int(1 / scale_factor) - (w % int(1 / scale_factor))
            if h % int(1 / scale_factor) != 0:
                pad_h = int(1 / scale_factor) - (h % int(1 / scale_factor))

            if pad_w != 0 or pad_h != 0:
                x = x.permute(0, 3, 1, 2)
                x = F.pad(x, (0, pad_h, 0, pad_w))
                x = x.permute(0, 2, 3, 1)
                w = w + pad_w
                h = h + pad_h

            new_h = int(h * scale_factor)
            new_c = int(c / scale_factor)
            x = x.reshape(n, w, new_h, new_c)
            x = x.permute(0, 2, 1, 3).contiguous()
            new_w = int(w * scale_factor)
            new_c_final = int(c / (scale_factor * scale_factor))
            x = x.view(n, new_h, new_w, new_c_final)
            x = x.permute(0, 2, 1, 3).contiguous()
            return x


class PixelShuffleConnector(nn.Module):
    def __init__(self, in_hidden_size, out_hidden_size, down_rate=2, conv_before=False):
        super(PixelShuffleConnector, self).__init__()
        # ffn_hidden_size = 13696
        ffn_hidden_size = in_hidden_size * (
            down_rate**2
        )  # out_hidden_size * 4 3584 * 4 = 14336
        self.linear_proj = GLU(
            hidden_size=out_hidden_size,
            ffn_hidden_size=ffn_hidden_size,
            in_features=in_hidden_size * (down_rate**2),
        )
        rank0_print(
            f"==> pixelshuffle: ffn_hidden_size: {ffn_hidden_size}, in_features: {in_hidden_size * (down_rate**2)}"
        )
        self.down_rate = down_rate
        self.downsample = PixelShuffleLayer()
        self.conv_before = conv_before
        if conv_before:
            self.conv = nn.Conv2d(
                in_channels=in_hidden_size,
                out_channels=in_hidden_size,
                kernel_size=2,
                stride=2,
            )

    def forward(self, x, attention_mask: torch.Tensor = None, image_sizes=None):
        # print(f"xin: {x.shape}")
        if len(x.shape) == 3:
            b, s, h = x.shape
            if image_sizes is not None:
                grid_size = image_sizes
                # tensor([[121,  19], [ 48,  48], [ 41,  55], [ 39,  59]])
                # making the output is a list
                x_list = []
                for i, sz in enumerate(image_sizes):
                    # patch_size for siglip2 forcely
                    a = x[i][: sz[0] * sz[1], :]
                    # print(a.shape)
                    a = a.reshape(1, sz[0], sz[1], h)
                    a = self.downsample(a, scale_factor=1 / self.down_rate)
                    a = a.reshape(1, -1, a.shape[-1])
                    a = self.linear_proj(a)
                    x_list.append(a.squeeze(0))
                return x_list
            else:
                grid_size = int(s**0.5)
            x = x.reshape(b, grid_size, grid_size, h)
            x = self.downsample(x, scale_factor=1 / self.down_rate)
        elif len(x.shape) == 4:
            if self.conv_before:
                # only for 4x4 at least?
                # print(f'brefore conv: {x.shape}')
                x = self.conv(x.permute(0, 3, 1, 2)).permute(0, 2, 3, 1)
            # print(x.shape)
            x = self.downsample(x, scale_factor=1 / self.down_rate)
        else:
            raise ValueError(f"Unsupported input shape: {x.shape}, either rank 3 or 4")
        # print(f"x after pixshuffle: {x.shape}")
        # [11, 16, 16, 4608]
        x = x.reshape(x.shape[0], -1, x.shape[-1])
        # print(f"x after pixshuffle: {x.shape}")
        x = self.linear_proj(x)
        return x


def get_pixel_shuffle(type_name, mm_hidden_size, hidden_size):
    resampler_match = re.match(r"^pixelshuffle_(\d+)x$", type_name)
    if resampler_match:
        down_rate = int(resampler_match.group(1))
        rank0_print(
            f"==> conn_ve_llm type: {type_name}, downsample rate: {down_rate}, {mm_hidden_size}->{hidden_size}"
        )
        m = PixelShuffleConnector(
            in_hidden_size=mm_hidden_size,
            out_hidden_size=hidden_size,
            down_rate=down_rate,
        )
        return m
    else:
        raise ValueError(f"Unknown resampler type: {type_name}")
