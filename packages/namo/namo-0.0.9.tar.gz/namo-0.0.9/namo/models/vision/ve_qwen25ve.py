import os
from .ve_base import BaseVE
from loguru import logger
from namo.utils.utils import is_main_process
from transformers.models.qwen2_5_vl.modeling_qwen2_5_vl import (
    Qwen2_5_VisionTransformerPretrainedModel,
)
from transformers.models.qwen2_5_vl.configuration_qwen2_5_vl import (
    Qwen2_5_VLVisionConfig,
    Qwen2_5_VLConfig,
)
from transformers import AutoProcessor
import torch
from transformers.models.qwen2_5_vl.processing_qwen2_5_vl import Qwen2_5_VLProcessor


class Qwen2_5_VL_VE(BaseVE):
    def _load_vision_tower(self):
        # other models can be customized here, normally AutoModel can handle well
        if (
            os.path.exists(self.vision_tower_name)
            and "output/" not in self.vision_tower_name
        ):
            config = Qwen2_5_VLConfig.from_pretrained(self.vision_tower_name)
            self.vision_tower = (
                Qwen2_5_VisionTransformerPretrainedModel.from_pretrained(
                    self.vision_tower_name,
                    config=config,
                    ignore_mismatched_sizes=True,
                    torch_dtype=self.torch_dtype,
                    attn_implementation="flash_attention_2",
                )
            )
            if is_main_process():
                logger.info(
                    f"creating Qwen2.5VL-VE model from local: {self.vision_tower_name}"
                )
        else:
            if is_main_process():
                logger.info(
                    f"creating Qwen2.5VL-VE model: {self.vision_tower_name} vision_config: {self.vision_config}"
                )
                # logger.info(f"creating Qwen2.5VL-VE model: {self.vision_tower_name} <- empty")
            self.vision_tower = Qwen2_5_VisionTransformerPretrainedModel(
                config=self.vision_config,
            )

    def _load_image_processor(self):
        processor_path = self.vision_tower_name
        logger.info(f"loading image processor from: {self.vision_tower_name}")
        if os.path.exists(self.vision_tower_name):
            processor_path = self.vision_tower_name
        elif os.path.exists(self.model_name_or_path):
            processor_path = self.model_name_or_path
        else:
            logger.info(
                f"No processor found for either {self.vision_tower_name} or {self.model_name_or_path}"
            )
        try:
            logger.info(f'load image processor from: {processor_path}')
            self.image_processor = AutoProcessor.from_pretrained(
                processor_path, trust_remote_code=True
            )
        except Exception as e:
            logger.info(f"Failed to load processor from {processor_path}: {e}")
            logger.info("Trying to use processor from Qwen2_5_VLProcessor")
            self.image_processor = Qwen2_5_VLProcessor.from_pretrained(processor_path)

    def feature_select(self, image_forward_outs):
        # no select, just return last hidden state
        return image_forward_outs

    def forward(self, images, pixel_attention_mask=None, spatial_shapes=None):
        # print(images)
        # print(f'==> image shape: {images.shape}')
        # print(f'==> spatial shape: {spatial_shapes.shape}')
        # print(f'==> spatials: {spatial_shapes}')
        out = self.basic_forward(images, pixel_attention_mask, spatial_shapes)
        # print(spatial_shapes)
        # print(out.shape)
        # token_norms = torch.norm(out, p=2, dim=-1)
        # print(f'token_norms: {token_norms}') # [146.0000, 135.0000,  48.2500\
        # visual tokens seems very big
        # print(out)
        # [[1,34,45],[1,36,45]]
        # out: [3456,1152]
        chunk_sizes = torch.prod(spatial_shapes, dim=1).tolist()
        # TODO: consider video: [[1,22,31],[5,23,22]]
        # print(chunk_sizes)
        out = torch.split(out, [c // 4 for c in chunk_sizes], dim=0)
        # print(out[0].shape)
        return list(out)

    def _get_features(self, inputs, pixel_attention_mask=None, spatial_shapes=None):
        # print(f'image shape: {inputs.shape}')
        # print(f'spatial shape: {spatial_shapes.shape}')
        # print(f'spatials: {spatial_shapes}')
        outputs = self.vision_tower(inputs, spatial_shapes)
        feas = self.feature_select(outputs).to(inputs.dtype)
        # print(f'vision feas: {feas.shape}')
        return feas
