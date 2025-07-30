"""

A unified API interface support various VL models


"""

from namo.api.qwen2_5_vl import Qwen2_5_VL
from .namo import NamoVL
from .hydra import NamoHydraVL

from loguru import logger


class VLInfer:
    def __init__(self, model_type="qwen2.5-vl", model_path=None, device="auto"):
        if (
            "qwen2.5-vl" in model_type
            or model_path is not None
            and "qwen" in model_path.lower()
            and "qwen3" not in model_path.lower()
        ):
            logger.info(f"initial Qwen2.5 VL from: {model_path}")
            self.model = Qwen2_5_VL(model_path=model_path)
        elif "hydra" in model_type.lower():
            self.model = NamoHydraVL(model_path=model_path)
        elif "namo" in model_type.lower():
            self.model = NamoVL(device=device)

        else:
            raise ValueError(f"Unknown model type: {model_type}")

    def generate(self, prompt, images, verbose=False, enable_thinking=False):
        self.model.generate(
            prompt, images, verbose=verbose, enable_thinking=enable_thinking
        )
