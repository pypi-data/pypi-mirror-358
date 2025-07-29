from typing import List, Tuple, Union
from torch import nn
import torch
import re
from namo.models.modal_adapt.adapt_ve.mlp import MLP
from namo.models.modal_adapt.adapt_ve.components import MlpGLU
from namo.models.modal_adapt.adapt_ve.pixelshuffle import get_pixel_shuffle
from namo.utils.utils import rank0_print


class ConnVE(nn.Module):
    def __init__(self, config):
        super().__init__()

        self.config = config
        type_name = self.config.conn_ve_llm_type
        self.type_name = type_name

        llm_hidden_size = config.text_config.hidden_size
        ve_hidden_size = getattr(
            config.vision_config, "hidden_size", config.vision_config.intermediate_size
        )
        if getattr(config.vision_config, "out_hidden_size") is not None:
            ve_hidden_size = getattr(config.vision_config, "out_hidden_size")
        rank0_print(
            f"==> current conn type: {type_name}, ve_hidden_size: {ve_hidden_size}, llm_hidden_size: {llm_hidden_size}"
        )
        if type_name == "identity":
            modules = nn.Identity()
        elif type_name == "linear":
            modules = nn.Linear(ve_hidden_size, llm_hidden_size)
        elif "gelu" in type_name:
            modules = MLP(type_name, ve_hidden_size, llm_hidden_size)
        elif "pixelshuffle" in type_name:
            modules = get_pixel_shuffle(type_name, ve_hidden_size, llm_hidden_size)
        elif "ovis" in type_name:
            print(f"{type_name} is not supported")
        elif "glu" in type_name:
            rank0_print("==> Using MLP GLU.")
            modules = MlpGLU(
                in_hidden_size=ve_hidden_size, out_hidden_size=llm_hidden_size
            )
            # modules = nn.Sequential(*[m])
        else:
            raise ValueError(f"Unknown projector type: {type_name}")
        self.layers = modules

    def forward(
        self,
        x_or_tuple: Union[
            Tuple[torch.Tensor, torch.Tensor], torch.Tensor, List[torch.Tensor]
        ],
        image_sizes=None,
    ):
        x = x_or_tuple
        if isinstance(x, list):
            out = [self.layers(i, image_sizes=image_sizes) for i in x]
            # dynamic size input, out should be a list
            return out
        else:
            # hack
            if self.type_name == "glu":
                out = self.layers(x)
            else:
                out = self.layers(x, image_sizes=image_sizes)
            return out
