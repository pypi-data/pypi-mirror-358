from transformers import AutoConfig, AutoModel
from namo.models.vision.aimv2.configuration_aimv2 import AIMv2Config
from namo.models.vision.aimv2.modeling_aimv2 import AIMv2Model
from namo.models.vision.aimv2.modeling_aimv2_native import (
    AIMv2Model as AIMv2ModelNative,
)
from namo.processor import *
from .siglip.siglip2 import NamoSiglip2VisionModel, NamoSiglip2VisionConfig

AutoConfig.register("aimv2", AIMv2Config)
AutoConfig.register("siglip2_vision_model", NamoSiglip2VisionConfig)
