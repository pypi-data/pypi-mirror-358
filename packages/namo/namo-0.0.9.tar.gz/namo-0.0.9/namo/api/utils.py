import os
from namo.models.symbols import (
    DEFAULT_IMAGE_TOKEN_QWENVL,
    VISION_START_TOKEN,
    VISION_END_TOKEN,
    DEFAULT_IMAGE_TOKEN,
)


def replace_qwenvl_image_token_to_llava(s):
    # return s.replace(f'{VISION_START_TOKEN}{DEFAULT_IMAGE_TOKEN_QWENVL}{VISION_END_TOKEN}', DEFAULT_IMAGE_TOKEN)
    return s.replace(
        f"{VISION_START_TOKEN}{DEFAULT_IMAGE_TOKEN_QWENVL}{VISION_END_TOKEN}",
        f"{VISION_START_TOKEN}{DEFAULT_IMAGE_TOKEN}{VISION_END_TOKEN}",
    )
