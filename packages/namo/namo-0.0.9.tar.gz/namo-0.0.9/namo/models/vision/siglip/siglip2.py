try:
    from transformers.models.siglip2 import Siglip2VisionModel
    from transformers.models.siglip2 import Siglip2VisionConfig
except ImportError as e:
    print("siglip2 disabled as you need install transformers up to git main for now.")
from torch import nn
import torch
from loguru import logger


class RMSNorm(nn.Module):
    def __init__(self, hidden_size, eps=1e-6):
        """
        Qwen2RMSNorm is equivalent to T5LayerNorm
        """
        super().__init__()
        self.weight = nn.Parameter(torch.ones(hidden_size))
        self.variance_epsilon = eps

    def forward(self, hidden_states):
        input_dtype = hidden_states.dtype
        hidden_states = hidden_states.to(torch.float32)
        variance = hidden_states.pow(2).mean(-1, keepdim=True)
        hidden_states = hidden_states * torch.rsqrt(variance + self.variance_epsilon)
        return self.weight * hidden_states.to(input_dtype)

    def extra_repr(self):
        return f"{tuple(self.weight.shape)}, eps={self.variance_epsilon}"


class VLPatchMerger(nn.Module):
    def __init__(self, dim: int, num_patches: int) -> None:
        super().__init__()
        self.hidden_size = num_patches * 4
        self.ln_q = RMSNorm(num_patches, eps=1e-6)
        self.mlp = nn.Sequential(
            nn.Linear(num_patches, self.hidden_size),
            nn.GELU(),
            nn.Linear(self.hidden_size, dim),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.mlp(self.ln_q(x.permute((0, 2, 1))))
        return x.permute((0, 2, 1))


class NamoSiglip2VisionConfig(Siglip2VisionConfig):

    def __init__(
        self,
        hidden_size=768,
        intermediate_size=3072,
        num_hidden_layers=12,
        num_attention_heads=12,
        num_channels=3,
        num_patches=256,
        patch_size=16,
        hidden_act="gelu_pytorch_tanh",
        layer_norm_eps=0.000001,
        attention_dropout=0,
        num_visual_tokens=578,
        **kwargs,
    ):
        super().__init__(
            hidden_size,
            intermediate_size,
            num_hidden_layers,
            num_attention_heads,
            num_channels,
            num_patches,
            patch_size,
            hidden_act,
            layer_norm_eps,
            attention_dropout,
            **kwargs,
        )
        self.num_visual_tokens = num_visual_tokens


class NamoSiglip2VisionModel(Siglip2VisionModel):

    def __init__(self, config: NamoSiglip2VisionConfig):
        super().__init__(config)

        self.num_visual_tokens = (
            config.num_visual_tokens if hasattr(config, "num_visual_tokens") else 578
        )
        if self.num_visual_tokens > 0:
            self.patch_merger = VLPatchMerger(
                self.num_visual_tokens, config.num_patches
            )
            logger.info(
                f"==> num_patches: {config.num_patches} -> num_visual_tokens: {self.num_visual_tokens}"
            )
        else:
            logger.info(
                f"==> patch merger turned off. we will using pixelshuffle to reduce tokens."
            )

    def forward(
        self,
        pixel_values,
        pixel_attention_mask,
        spatial_shapes,
        output_attentions=None,
        output_hidden_states=None,
        return_dict=None,
    ):
        outputs = super().forward(
            pixel_values,
            pixel_attention_mask,
            spatial_shapes,
            output_attentions,
            output_hidden_states,
            return_dict,
        )
        # print(outputs)
        # print(outputs.last_hidden_state.shape)
        # print(outputs.pooler_output.shape)
        if self.num_visual_tokens > 0:
            outputs = self.patch_merger(outputs.last_hidden_state)
            # print(outputs.shape)
            return outputs
        else:
            return outputs.last_hidden_state
