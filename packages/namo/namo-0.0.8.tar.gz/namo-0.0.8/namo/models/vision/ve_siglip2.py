import os
from .ve_base import BaseVE
from loguru import logger
from namo.utils.utils import is_main_process
from . import NamoSiglip2VisionModel, NamoSiglip2VisionConfig


class Siglip2VE(BaseVE):
    def _load_vision_tower(self):
        # other models can be customized here, normally AutoModel can handle well
        if os.path.exists(self.vision_tower_name):
            config = NamoSiglip2VisionConfig.from_pretrained(self.vision_tower_name)
            config.num_patches = self.num_patches_from_config
            config.num_visual_tokens = self.num_visual_tokens_from_config
            if is_main_process():
                logger.info(
                    f"loading Siglip2 pretrain model: {self.vision_tower_name} {self.torch_dtype}, num_patches: {config.num_patches}"
                )
            self.vision_tower = NamoSiglip2VisionModel.from_pretrained(
                self.vision_tower_name,
                config=config,
                ignore_mismatched_sizes=True,
                torch_dtype=self.torch_dtype,
                attn_implementation="flash_attention_2",
            )
        else:
            if is_main_process():
                logger.info(f"creating Siglip2 model: {self.vision_tower_name}")
            self.vision_tower = NamoSiglip2VisionModel(
                config=self.vision_config,
            )

    def feature_select(self, image_forward_outs):
        # no select, just return last hidden state
        return image_forward_outs

    def forward(self, images, pixel_attention_mask=None, spatial_shapes=None):
        return self.basic_forward(images, pixel_attention_mask, spatial_shapes)
