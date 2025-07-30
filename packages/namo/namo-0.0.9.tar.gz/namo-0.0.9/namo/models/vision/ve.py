from namo.models.vision.ve_aim import AimV2VE
from namo.models.vision.ve_siglip_navit import SigLipNavitVE
from torch import nn
from namo.models.vision.ve_siglip2 import Siglip2VE
from namo.models.vision.ve_qwen25ve import Qwen2_5_VL_VE


def get_ve(config, **kwargs):
    type_name = config.vision_config._name_or_path.lower()
    if type_name == None or type_name == "":
        type_name = config.vision_config.model_type

    if "siglip2" in type_name.lower():
        return Siglip2VE(config, **kwargs)
    elif "siglip" in type_name and "navit" not in type_name:
        return SigLipNavitVE(config, **kwargs)
    elif "aim" in type_name:
        return AimV2VE(config, **kwargs)
    elif "qwen2.5-vl" in type_name or "qwen2_5_vl" in type_name:
        return Qwen2_5_VL_VE(config, **kwargs)
    else:
        raise ValueError(f"Unsupported vision model: {type_name}")
